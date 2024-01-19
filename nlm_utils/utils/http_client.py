import asyncio
import sys

from aiohttp import ClientSession
from dataclasses import dataclass  # noreorder
from typing import Any

from concurrent.futures import ThreadPoolExecutor
import pickle

import logging
import json


@dataclass
class HttpRequstData:
    url: str
    method: str
    data: Any = None


class AsyncHttpClient:
    def __init__(self, out_protocal="text", in_protocal="text", header=None):
        self.tasks = []
        self.header = header
        self.in_protocal = in_protocal
        self.out_protocal = out_protocal

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def _prepare_data(self, data):
        if data is None:
            return None
        if self.in_protocal == "text":
            return data
        elif self.in_protocal == "json":
            return json.dumps(data)
        elif self.in_protocal == "pickle":
            return pickle.dumps(data, protocol=4)
        else:
            raise RuntimeError(f"Can not process output protocal {self.out_protocal}")

    def post(self, url, data=None):
        data = self._prepare_data(data)
        task = HttpRequstData(url=url, method="post", data=data)
        self.tasks.append(task)

    def get(self, url, data=None):
        data = self._prepare_data(data)
        task = HttpRequstData(url=url, method="get", data=data)
        self.tasks.append(task)

    def run(self):
        self.logger.info(f"AsyncHttpClient receives {len(self.tasks)} tasks")
        # execute the requests in a thread to bypass async event loop in univorn
        with ThreadPoolExecutor() as executor:
            future = executor.submit(self.async_worker)
            responses = future.result()

        return responses

    def async_worker(self):
        # disable garbage collection in async_worker thread
        import gc

        gc.disable()
        coroutines = self._run_batch()

        # Emulate asyncio.run() on older versions
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = None
        try:
            results = loop.run_until_complete(coroutines)
        finally:
            loop.close()
            asyncio.set_event_loop(None)
        gc.enable()
        return results

    async def _run_batch(self):
        # run individual task and return a coroutine task
        async def _run(session, task):
            if task.method == "get":
                return await session.get(task.url, data=task.data)
            elif task.method == "post":
                return await session.post(task.url, data=task.data)
            else:
                NotImplementedError(f"Method {task.method} is not implemented")

        # create coroutines
        async with ClientSession() as session:
            coroutines = []
            for task in self.tasks:
                if sys.version_info >= (3, 7):
                    coroutine = asyncio.create_task(_run(session, task))
                else:
                    coroutine = asyncio.ensure_future(_run(session, task))

                coroutines.append(coroutine)

            responses = []
            # get response
            for response in await asyncio.gather(*coroutines):
                if self.out_protocal == "text":
                    responses.append(await response.text())
                elif self.out_protocal == "json":
                    responses.append(await response.json())
                elif self.out_protocal == "binary":
                    responses.append(await response.read())
                elif self.out_protocal == "pickle":
                    responses.append(pickle.loads(await response.read()))
                else:
                    raise RuntimeError(
                        f"Can not process output protocal {self.out_protocal}",
                    )
            await session.close()

        return responses
