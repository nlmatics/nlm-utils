from collections import OrderedDict
from time import time

from .base_agent import BaseAgent


class MemoryCacheData:
    def __init__(self, data, ttl):
        self._data = data
        self._ttl = ttl
        self._last_access = time()

    def get_data(self):
        self._last_access = time()
        return self._data

    def is_expired(self):
        return time() - self._last_access > self._ttl


class MemoryAgent(BaseAgent):
    __name__ = "MemoryAgent"

    def __init__(self, prefix: str = None, max_size: int = 1024, ttl: int = 3600):
        super().__init__()
        # setting parameters
        self._max_size = max_size
        self._ttl = ttl
        # create data
        self._data = OrderedDict()
        self.logger.info(f"MemoryAgent will save cache to {self._max_size}")
        # prefix of the cache key

    def connect(self):
        self.connected = True

    def reset(self):
        self._data.clear()

    def read(self, cache_key):
        cache_key = f"{cache_key}"
        if cache_key in self._data:
            # check TTL
            if self._data[cache_key].is_expired():
                # current cache_key is expired, and _data is LRU
                # this means all keys before cache_key is also expired
                for _ in range(len(self._data)):
                    key, _ = self._data.popitem(last=False)
                    if key == cache_key:
                        break
                return False, None
            # update LRU
            self._data.move_to_end(cache_key)
            # return cache
            return True, self._data[cache_key].get_data()
        else:
            return False, None

    def write(self, serilized_data, cache_key):
        # max_size enabled
        if self._max_size and len(self._data) >= self._max_size:
            key = next(iter(self._data))
            del self._data[key]

        self._data[cache_key] = MemoryCacheData(serilized_data, self._ttl)

    def delete(self, cache_key):
        del self._data[cache_key]
