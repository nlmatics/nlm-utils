from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from .base_agent import BaseAgent


class MongodbAgent(BaseAgent):
    __name__ = "MongodbAgent"

    def __init__(
        self,
        db,
        collection,
        host: str = "localhost",
        port: int = 27017,
    ):
        super().__init__()
        self._host = host
        self._port = port if isinstance(port, int) else int(port)
        # prefix of the cache key
        self._db = db
        self._collection = collection

    def connect(self):
        # client already connected
        if self.connected:
            try:
                self.client.admin.command("ismaster")
                return
            except ConnectionFailure:
                self.connected = False
                self.logger.error(
                    f"Failed to connect to Mongodb {self._host}:{self._port}, reconnecting",
                )

        try:
            # connect client
            self.client = MongoClient(self._host, self._port)
            self.client.admin.command("ismaster")
            self.collection = self.client[self._db][self._collection]
            # ensure index
            self.collection.create_index("cache_key", name="cache_key", unique=True)
            self.connected = True
        except ConnectionFailure:
            self.connected = False
            self.logger.error(f"Failed to connect to Mongodb {self._host}:{self._port}")

    def reset(self):
        self.collection.drop()

    def read(self, cache_key):
        data = self.collection.find_one(cache_key)
        if data:
            serilized_data = data["serilized_data"]
            return True, serilized_data
        else:
            return False, None

    def write(self, serilized_data, cache_key):
        data = {"cache_key": cache_key, "serilized_data": serilized_data}
        self.collection.update_one(
            {"cache_key": cache_key},
            {"$set": data},
            upsert=True,
        )

    def delete(self, cache_key):
        self.collection.delete_one({"cache_key": cache_key})
