#!/usr/bin/python3

from urllib.parse import urlsplit
import asyncio
import aiofiles
import aiohttp
import traceback
from bs4 import BeautifulSoup


class UrlDownloader:

    def __init__(self, logger, output_directory):
        self.logger = logger
        self.output_directory = output_directory

    # get the link id at the end of the link, e.g. http://www.bahai.org/r/02857 -> 02857
    def parse_bahaiorg_linkid(self, url):
        return url.split("/")[-1]

    def parse_oceanoflights(self, url, tree, length_hint):
        # get top level container
        top_level_divs = tree.find_all('div', { 'class': 'tablet-content' })
        if len(top_level_divs) != 1:
            raise ValueError(f"Expected exactly one div with class 'library-document' but got {len(top_level_divs)}")
        top_level_div = top_level_divs[0]
        ps = top_level_div.find_all('p')

        # collect all the text
        text = ""
        for p in ps:
            text = text + p.text + "\n"

        return text

    def parse_oldreference(self, url, tree, length_hint):
        # get top level container
        text_divs = tree.find_all('div', { 'class': 'Stext2' })

        # collect all the text
        text = ""
        for div in text_divs:
            links = div.find_all('a')
            for link in links:
                link.decompose()
            text = text + div.text + "\n"

        return text

    # check if this is the prayers and meditation compilation so that we can
    # use separate paring logic for that
    #
    # https://www.bahai.org/fa/library/authoritative-texts/bahaullah/prayers-meditations/1#198178094
    #
    def check_pmp(self, tree):
        unique_href = "/fa/library/authoritative-texts/bahaullah/prayers-meditations/1#198178094"
        link_tag = tree.find('a', {'href': unique_href})
        return bool(link_tag)

    def parse_bahaiorg(self, url, tree, length_hint):

        # figure out if we're dealing with this specific compilation
        isPmp = self.check_pmp(tree)

        # get the linkid
        linkid = self.parse_bahaiorg_linkid(url)

        # get top level container
        top_level_divs = tree.find_all('div', { 'class': 'library-document' })
        if len(top_level_divs) != 1:
            raise ValueError(f"Expected exactly one div with class 'library-document' but got {len(top_level_divs)}")
        top_level_div = top_level_divs[0]
        ps = top_level_div.find_all('p')

        # find the <p> in which the text starts (marked by <a>)
        first_index = None
        for i, p in enumerate(ps):
            sublinks = p.find_all('a')
            for sublink in sublinks:
                if not sublink.has_attr('class'):
                    continue
                if not sublink.has_attr('id'):
                    continue
                if not 'brl-location' in sublink.get('class'):
                    continue 
                if str(sublink.get('id')) == str(linkid):
                    first_index = i

        if first_index is None:
            raise ValueError(f"Could not find linkid {linkid} on page")

        ps = ps[first_index:]
        text = ""
        for p in ps:
            # remove any links
            links = p.find_all('a')
            for link in links:
                link.decompose()

            # remove superscripts
            sups = p.find_all('sup')
            for sup in sups:
                sup.decompose()

            # handle termination case for PMP compilation
            has_align_center = p.has_attr('class') and 'brl-align-center' in p.get('class')
            has_global_selection_number = p.has_attr('class') and 'brl-global-selection-number' in p.get('class')
            self.logger.debug(f"PMP={isPmp} HAC={has_align_center} HGSN={has_global_selection_number} len={len(text)}")
            if len(text) > 0 and has_align_center and isPmp:
                self.logger.debug("Invoking PMP termination case")
                break

            # handle termination case for "brl-global-selection-number"
            #   this is a reliable indication a new selection is starting
            if len(text) > 0 and has_global_selection_number:
                break

            # collect the text
            text = text + p.text + "\n"

        return text

    async def save_to_file(self, text, file_id):
        filename = f"{self.output_directory}/{file_id}.txt"
        
        async with aiofiles.open(filename, 'w') as f:
            await f.write(text)

    async def download_html(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, allow_redirects=True) as response:

                if response.status == 200:
                    content = await response.text()
                    soup = BeautifulSoup(content, 'html.parser')
                    return soup
                else:
                    raise Exception(f"Received {response.status} downloading {url}")


    async def process_url(self, url, file_id, length_hint = 0):

        if url.startswith("http://"):
            url = f"https://{url[7:]}"

        urlparse = urlsplit(url)

        self.logger.debug(f"Going to download {url} to {file_id}.")
        if urlparse.hostname == "bahai.org" or urlparse.hostname == "www.bahai.org":
            parser = self.parse_bahaiorg
        elif urlparse.hostname == "oceanoflights.org":
            parser = self.parse_oceanoflights
        elif urlparse.hostname == "reference.bahai.org":
            parser = self.parse_oldreference
        else:
            self.logger.log(f"Could not process URL {url} for {file_id}; no parsers matched.")
            return None

        tree = await self.download_html(url)

        try:
            text = parser(url, tree, length_hint)
        except Exception as e:
            self.logger.log(f"Error parsing {url} for {file_id}.\n{traceback.format_exc()}") 
            return None

        if len(text) == 0:
            self.logger.log(f"Error parsing {url} for {file_id}: parser returned with no content.")
            return None

        await self.save_to_file(text, file_id)
        self.logger.log(f"Downloaded and parsed {url}; got {len(text)} characters and saved to {file_id}.")
        return text


async def url_download(args, logger):
    downloader = UrlDownloader(logger, ".")
    await downloader.process_url(args.url, args.file, args.length_hint)
