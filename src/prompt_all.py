import asyncio
import aiofiles
import functools
import re

from src.input import Input
from src.logger import Logger
from src.gpt import GPT
from src.worker_pool import AsyncWorkerPool
from src.template import Template
from src.translation_helper import TranslationHelper

class PromptAll:
    def __init__(self, args, logger, data, gpt):
        self.args = args
        self.logger = logger
        self.data = data
        self.gpt = gpt

        self.output_data = {}
        self.next_to_write = 0
        self._output_lock = asyncio.Lock()
        self.workers = args.workers


        self.translation_helper = TranslationHelper(args, logger)

    async def prompt_all(self):
        # Load input text
        input_text = self.data.get_text_lines()

        # Get the prompt
        try:
            with open(self.args.prompt, 'r') as f:
                prompt_text = f.read()
        except e:
            self.logger.fatal_error(e)

        await self.logger.log_async(f"Prompt: {prompt_text}")
        template = Template(self.args, self.logger, prompt_text)

        await self._launch_jobs(input_text, template)

    async def callback(self, output, index, total_lines):
        self.output_data[index] = output
        await self.logger.debug_async("callback with index=" + str(index) + " output=" + output)
        await self.logger.log_async(f"result: {index} -> {output}")

        async with self._output_lock:
            while self.next_to_write < total_lines:
                if self.next_to_write in self.output_data.keys():
                    next_answer = self.output_data[self.next_to_write]
                    await self.logger.debug_async("writing index " + str(self.next_to_write))
                    await self.logger.output_async(next_answer)
                    self.next_to_write = self.next_to_write + 1
                else:
                    break

    async def _launch_jobs(self, input_text, template):
        # launch the jobs
        pool = AsyncWorkerPool(worker_count=self.workers, logger=self.logger)
        await pool.start()

        for index, line in enumerate(input_text):
            callback = functools.partial(self.callback, total_lines=len(input_text), index=index)
            await pool.add_task(self._run_prompt, line, template, callback=callback)

        await pool.join()

    def _count_words(self, text):
        return len(text.split())

    async def _run_prompt(self, input_text, template):
        variables = await self.translation_helper.get_variables(input_text)
        prompt = template.expand(variables)
        await self.logger.log_async("[_run_prompt] prompt: " + prompt)


        result = await self.gpt.query(system=prompt, user=input_text)
        result = result.replace("\n","\t")
        return result

async def prompt_all(args, logger):
    data = Input(args, logger)
    gpt = GPT(args, logger)
    manager = PromptAll(args, logger, data, gpt)
    await manager.prompt_all()
