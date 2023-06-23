import os
import asyncio
import aiofiles
import traceback
import sys

class Logger:

    def __init__(self, args):
        self.output_filename = args.output
        self.log_filename = args.output + ".log"
        self.debug_mode = args.debug

    # Synchronous methods

    def output(self, message):
        with open(self.output_filename, 'a') as output_file:
            output_file.write(str(message) + '\n')
            output_file.flush()

        self.log(message)
        print(message)

    def log(self, message):
        with open(self.log_filename, 'a') as log_file:
            log_file.write(str(message) + '\n')
            log_file.flush()

    def debug(self, message):
        if self.debug_mode:
            self.log("DEBUG: " + str(message) )
            print("DEBUG: " + str(message))

    def error(self, e):
        self.output(f"Error: {e}")
        self.output(traceback.format_exc())

    def fatal_error(self, e):
        self.output(f"Fatal: {e}")
        self.output(traceback.format_exc())
        sys.exit(1)

    # Asynchronous methods

    async def output_async(self, message):
        async with aiofiles.open(self.output_filename, 'a') as output_file:
            await output_file.write(str(message) + '\n')
            await output_file.flush()

        await self.log_async(message)
        print(message)

    async def log_async(self, message):
        async with aiofiles.open(self.log_filename, 'a') as log_file:
            await log_file.write(str(message) + '\n')
            await log_file.flush()

    async def debug_async(self, message):
        if self.debug_mode:
            await self.log_async("DEBUG: " + str(message))
            print("DEBUG: " + message)
