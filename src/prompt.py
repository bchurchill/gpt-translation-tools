import asyncio
import aiofiles
import functools

from src.input import Input
from src.gpt import GPT
from src.worker_pool import AsyncWorkerPool

class PromptOne:
    def __init__(self, args, logger, data, gpt):
        self.logger = logger
        self.args = args
        self.gpt = gpt
        self.data = data

    async def prompt_one(self):

        # Load input text
        input_text = self.data.get_text()
        result = await self.gpt.query(None, input_text)
        await self.logger.output_async(result)

async def prompt_one(args, logger):
    data = Input(args, logger)
    gpt = GPT(args, logger)
    manager = PromptOne(args, logger, data, gpt)
    await manager.prompt_one()
