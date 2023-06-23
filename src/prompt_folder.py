import asyncio
import aiofiles
import functools
import re
import os

from src.input import Input
from src.logger import Logger
from src.gpt import GPT
from src.worker_pool import AsyncWorkerPool
from src.template import Template
from src.translation_helper import TranslationHelper

class PromptFolder:
    def __init__(self, args, logger, gpt):
        self.args = args
        self.logger = logger
        self.gpt = gpt

        self.next_to_write = 0
        self._output_lock = asyncio.Lock()
        self.workers = args.workers

        self.translation_helper = TranslationHelper(args, logger)

    def get_txt_files(self, foldername):
        txt_files = []
        for f in os.scandir(foldername):
            if f.name.endswith(".txt"):
                filename = os.path.join(foldername, f.name)
                txt_files.append(filename)
        return txt_files

    async def prompt_folder(self):
        # Get the prompt
        try:
            with open(self.args.prompt, 'r') as f:
                prompt_text = f.read()
        except Exception as e:
            self.logger.fatal_error(e)

        # Setup the template
        await self.logger.log_async(f"Prompt: {prompt_text}")
        template = Template(self.args, self.logger, prompt_text)

        # Get the file names
        input_files = self.get_txt_files(self.args.input_dir)

        await self._launch_jobs(input_files, template)

    async def callback(self, output, fileid):
        await self.logger.log_async(f"result: {fileid} -> {output}")

        async with self._output_lock:
            await self.logger.output_async(f"{fileid}: {output}")

    async def _launch_jobs(self, input_files, template):
        # launch the jobs
        pool = AsyncWorkerPool(worker_count=self.workers, logger=self.logger)
        await pool.start()

        for filename in input_files:
            fileid = filename.split("/")[-1][:-4]
            callback = functools.partial(self.callback, fileid=fileid)
            await pool.add_task(self._run_prompt, filename, fileid, template, callback=callback)

        await pool.join()

    def _count_words(self, text):
        return len(text.split())

    async def _run_prompt(self, input_file, fileid, template):
        async with aiofiles.open(input_file, mode='r') as f:
            contents = await f.read()

        variables = await self.translation_helper.get_variables(contents, fileid)
        prompt = template.expand(variables)
        await self.logger.log_async("[_run_prompt] prompt: " + prompt)

        result = await self.gpt.query(system=prompt, user=contents)
        result = result.replace("\n","\t")
        return result

async def prompt_folder(args, logger):
    gpt = GPT(args, logger)
    manager = PromptFolder(args, logger, gpt)
    await manager.prompt_folder()
