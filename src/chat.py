import asyncio
import aiofiles
import functools
import sys

from src.input import Input
from src.gpt import GPT
from src.worker_pool import AsyncWorkerPool

class Chat:
    def __init__(self, args, logger, gpt):
        self.logger = logger
        self.args = args
        self.gpt = gpt

    async def show_dots(self):
        while True:
            print(".", end='', flush=True)
            await asyncio.sleep(0.5)
            

    def prompt_input(self):
        # provide the user with a graphical prompt
        input_lines = []
        while True:
            print(f"{self.args.model}> ", end='', flush=True)
            line = sys.stdin.readline()
            command = line.lower().strip()
            if command in ['end', 'go']:
                break
            if command in ['exit', 'quit'] and len(input_lines) == 0:
                return None
            input_lines.append(line)

        return '\n'.join(input_lines)
        

    async def chat(self):
        # Load prompt text
        prompt = self.args.prompt
        self.logger.log(f"Prompt: {prompt}")
        messages = [ { "role": "system", "content": prompt } ] 

        while True:
            # Get the next message
            next_message = self.prompt_input()

            # Check for termination
            if next_message == None:
                break

            # Start dot animation
            dots = asyncio.create_task(self.show_dots())

            messages.append( { "role": "user", "content": next_message } )
            self.logger.log(f"User: {next_message}")
            response = await self.gpt.query_history(messages)
            messages.append( { "role": "assistant", "content": response })

            # Show output
            dots.cancel()
            print("")
            self.logger.output(response)



async def chat(args, logger):
    gpt = GPT(args, logger)
    manager = Chat(args, logger, gpt)
    await manager.chat()
