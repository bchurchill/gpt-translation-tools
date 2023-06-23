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

# Idea is that we are given:
# (1) an input folder of texts
# (2) a "map" prompt which is applied to each line individually of each text
# (3) a "reduce" prompt that is applied to the outputs of the mapping step

class MapReduce:
    def __init__(self, args, logger, gpt):
        self.args = args
        self.logger = logger
        self.gpt = gpt
        self.workers = args.workers

        self._output_data = {}
        self._map_done = {}
        self._output_lock = {}
        self._global_lock = asyncio.Lock()

        self.translation_helper = TranslationHelper(args, logger)

    async def map_reduce(self):
        # Get the list of files
        file_data = []
        input_filenames = self._get_txt_files(self.args.input_dir)
        for path in input_filenames:
            filename = os.path.basename(path)
            fileid = filename[:-4]
            filedata = {
                "filename": filename,
                "path": path,
                "id": fileid
            }
            self.logger.debug(filedata)
            file_data.append(filedata)

        # Get the mapping prompt
        try:
            with open(self.args.map_prompt, 'r') as f:
                self.map_prompt = f.read()
        except e:
            self.logger.fatal_error(e)

        # Get the reduce prompt
        try:
            with open(self.args.reduce_prompt, 'r') as f:
                self.reduce_prompt = f.read()
        except e:
            self.logger.fatal_error(e)

        # Setup the pool
        self.pool = AsyncWorkerPool(self.workers, self.logger)
        await self.pool.start()

        # Run the mapping step for each file in its own queue
        #  (once some finish it will invoke the reduce step)
        for data in file_data:
            await self._start_map_jobs(data["id"], data["path"])

        await self.pool.join()

    def _get_txt_files(self, foldername):
        txt_files = []
        for f in os.scandir(foldername):
            if f.name.endswith(".txt"):
                filename = os.path.join(foldername, f.name)
                txt_files.append(filename)
        return txt_files

    async def _start_map_jobs(self, fileid, path):
        # Open the file
        try:
            with open(path, 'r') as f:
                file_contents = f.readlines()
        except Exception as e:
            self.logger.error(e)
            return 

        original_length = 0
        for line in file_contents:
            original_length += self._count_words(line)

        for index, line in enumerate(file_contents): 
            callback = functools.partial(self._map_callback, fileid=fileid, index=index, total_lines=len(file_contents), original_length = original_length)
            await self.pool.add_task(self._map, line, fileid, index, callback=callback)


    async def _map(self, text, fileid, index):
        # TODO: check if data is in cache

        variables = await self.translation_helper.get_variables(text, fileid)
        template = Template(self.args, self.logger, self.map_prompt)
        prompt = template.expand(variables)

        await self.logger.log_async("[_map] prompt: " + prompt)
        result = await self.gpt.query(prompt, text)
        result = result.replace("\n","\t")
        return result



    async def _map_callback(self, result, fileid, index, total_lines, original_length):
        
        # setup the data structures if we haven't already
        if not fileid in self._output_data:

            # only acquire global lock if we're touching the data structures
            async with self._global_lock:

                # check the condition again
                if not fileid in self._output_data:
                    self._map_done[fileid] = False
                    self._output_data[fileid] = {}
                    self._output_lock[fileid] = asyncio.Lock()

        ourmap = self._output_data[fileid]
        ourmap[index] = result
        await self.logger.log_async(f"[_map_callback] fileid={fileid} index={index} output={result}")

        # TODO: write data to cache

        async with self._output_lock[fileid]:

            hasIndex = [ i in ourmap for i in range(total_lines) ]
            hasAll = all(hasIndex)
            self.logger.debug(f"fileId={fileid} hasIndex={hasIndex} hasAll={hasAll} self._map_done[fileid]={self._map_done[fileid]}")

            if hasAll and not self._map_done[fileid]:
                self.logger.debug(f"Queue reduce for {fileid}")
                self._map_done[fileid] = True
                lines = [ ourmap[i] for i in range(total_lines) ]
                
                # queue reduce job
                await self.pool.add_task(self._reduce, fileid, lines, original_length, callback=None)



    # Applies the reduce prompt to the mapped data and returns the final output.
    async def _reduce(self, fileid, mapped_outputs, original_length):


        variables = {
            "AUTHOR": self.translation_helper.id_to_author(fileid)
        }
        template = Template(self.args, self.logger, self.reduce_prompt)
        prompt = template.expand(variables)
        await self.logger.log_async(f"[_reduce] prompt: {prompt}")
        data = "\n".join(mapped_outputs)
        result = await self.gpt.query(system=prompt, user=data)
        result = result.replace("\n","\t")
        self.logger.output(f"REDUCTION FOR {fileid}: {result}")
        return result

    def _count_words(self, text):
        return len(text.split())


async def map_reduce(args, logger):
    gpt = GPT(args, logger)
    manager = MapReduce(args, logger, gpt)
    await manager.map_reduce()
