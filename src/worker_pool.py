# worker_pool.py

import asyncio
import traceback
from typing import Any, Callable, List, Tuple

class AsyncWorkerPool:
    def __init__(self, worker_count: int, logger):
        self.worker_count = worker_count
        self.queue = asyncio.Queue()
        self.workers: List[asyncio.Task] = []
        self.logger = logger

    async def _worker(self):
        while True:
            task, args, callback = await self.queue.get()
            result = None
            try:
                result = await task(*args)
            except Exception as e:
                await self.logger.log_async(f"Error in worker: {e}")
                await self.logger.log_async(traceback.format_exc())

            try:
                if callback:
                    await callback(result)
            except Exception as e:
                await self.logger.log_async(f"Error in callback: {e}")
                await self.logger.log_async(traceback.format_exc())
            finally:
                self.queue.task_done()

    async def start(self):
        self.workers = [asyncio.create_task(self._worker()) for _ in range(self.worker_count)]

    async def add_task(self, task: Callable[..., Any], *args: Any, callback: Callable[[Any], None]):
        await self.queue.put((task, args, callback))

    async def join(self):
        await self.queue.join()
