#!/usr/bin/python3

from urllib.parse import urlsplit
import asyncio
import aiofiles
import aiohttp
import csv
import os
import re
from bs4 import BeautifulSoup
from src.url_downloader import UrlDownloader
from src.worker_pool import AsyncWorkerPool
from src.arabic_strings import ArabicStrings
from src.input import Input
from io import StringIO

class CsvDownloader:
    def __init__(self, args, logger, data):
        self.logger = logger
        self.data = data
        self.args = args
        self.output_directory = args.output_dir
        self.workers = args.workers

        self.arabic = ArabicStrings(logger)
        self.url_downloader = UrlDownloader(logger, self.output_directory)

    def validate_match(self, expected_prefix, downloaded, expected_wordcount):
        if len(downloaded) < len(expected_prefix):
            return (False, f"Validation failed: only got {len(downloaded)} bytes.", None, None)

        # truncate the download in case it's gigantic
        if len(downloaded) > 1000:
            actual = downloaded[0:1000]
        else:
            actual = downloaded

        # if there are elipses, then truncate
        expected_prefix = expected_prefix.split('...', 1)[0]
        expected_prefix = expected_prefix.split(chr(8230), 1)[0]

        # remove diacritical marks so that validation goes more smoothly
        expected_prefix = self.arabic.strip_diacritical(expected_prefix)
        actual = self.arabic.strip_diacritical(actual)

        # get alignment between the two strings
        diff, alignment = self.arabic.substring_distance(expected_prefix, actual)

        if diff >= 15:
            return (False, "Validation failed due to starting words.", diff, alignment)

        # count word
        aligned_download = downloaded[alignment:]
        actual_wordcount = self.wordcount(aligned_download)
        if expected_wordcount > actual_wordcount + 30 or expected_wordcount < actual_wordcount - 30:
            return (False, f"Validation failed due to wordcount.  Expected: {expected_wordcount}.  Got: {actual_wordcount}.", diff, alignment)

        # figure out if it's the same string
        return (True, f"Validation passed.", diff, alignment)


    async def run_one(self, url, fileid, expected_text, expected_wordcount):
        text = await self.url_downloader.process_url(url, fileid)

        if text is None:
            self.logger.log(f"No output for {fileid}")
            return

        validation_result = self.validate_match(expected_text, text, expected_wordcount)
        diff = validation_result[2]
        alignment = validation_result[3]
        self.logger.log(f"{validation_result[1]} for {fileid} with diff={diff} alignment={alignment}")


    async def callback(self, result):
        pass

    def wordcount(self, s):
        return len(s.split(" "))

    async def run(self):
        # Parse data from CSV file
        input_text = self.data.get_text_lines()
        csv_rows = [next(csv.reader(StringIO(line))) for line in input_text]

        # Figure out which column is which
        header = csv_rows[0]
        id_index = header.index("ID")
        url_index = header.index("Url")
        first_line_index = header.index("First line")
        word_count_index = header.index("Word count")
        csv_rows = csv_rows[1:]

        # start the worker pool
        pool = AsyncWorkerPool(worker_count=self.workers, logger=self.logger)
        await pool.start()

        # launch the jobs
        for index, line in enumerate(csv_rows):
            url = line[url_index]
            fileid = line[id_index]
            if "x" in fileid:
                fileid = f"index-{index+2}"
            first_line = line[first_line_index]
            expected_wordcount = int(line[word_count_index])
            await pool.add_task(self.run_one, url, fileid, first_line, expected_wordcount, callback=self.callback)

        await pool.join()


async def csv_download(args, logger):
    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)

    data = Input(args, logger)
    downloader = CsvDownloader(args, logger, data)
    await downloader.run()
