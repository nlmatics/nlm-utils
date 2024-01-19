from redis import Redis
from redis.exceptions import ConnectionError

from .base_agent import BaseAgent


class RedisAgent(BaseAgent):
    __name__ = "RedisAgent"

    def __init__(
        self,
        ttl: int = 3600,
        prefix: str = "tmp",
        host: str = "localhost",
        port: str = "6379",
        db: str = "0",
    ):
        super().__init__()
        self._host = host
        self._port = port
        self.db = db
        # prefix of the cache key
        self._prefix = prefix
        self._ttl = ttl
        self.logger.info(f"Redis cache agent is initilized with prefix: {self._prefix}")

    @property
    def connected(self):
        # if not self._connected:
        #     self.connect()
        return self._connected

    @connected.setter
    def connected(self, value):
        self._connected = value

    def connect(self):
        # client already connected
        if self._connected:
            return
        try:
            self.client = Redis(host=self._host, port=self._port, db=self.db)
            self.client.ping()
            self.connected = True
        except ConnectionError:
            self.logger.error(
                f"Can not connect to Redis server {self._host}:{self._port}.",
            )
            self._connected = False

    def reset(self):
        self.logger.debug(f"deleting redis keys with prefix {self._prefix}")
        for key in self.client.keys(f"{self._prefix}*"):
            self.logger.debug(f"Deleting {key} from Redis")
            self.client.delete(key)

    def read(self, cache_key):
        if self._prefix:
            cache_key = f"{self._prefix}-{cache_key}"

        # this can be problematic when cache result is None.
        serilized_data = self.client.get(cache_key)
        self.client.expire(cache_key, self._ttl)
        if serilized_data is not None:
            return True, serilized_data
        else:
            return False, None

    def write(self, serilized_data, cache_key):
        if self._prefix:
            cache_key = f"{self._prefix}-{cache_key}"
        if self._ttl:
            # set with expire time
            self.client.setex(cache_key, self._ttl, serilized_data)
        else:
            # set without expire time
            self.client.set(cache_key, serilized_data)

    def delete(self, cache_key):
        cache_key_in_db = cache_key
        if self._prefix:
            cache_key_in_db = f"{self._prefix}-{cache_key}"

        res = self.client.delete(cache_key_in_db)
        if res:
            self.logger.info(f"Deleting cache with key='{cache_key}'")
        else:
            self.logger.info(f"Cache not found wiht key='{cache_key}', skip deleting.")
