import os
from pathlib import Path
from tempfile import mkdtemp

from .base_agent import BaseAgent


class FileAgent(BaseAgent):
    __name__ = "FileAgent"

    def __init__(self, path: str = None, collection: str = None):
        super().__init__()

        if path:
            self.filepath = Path(path)
        else:
            self.filepath = Path(mkdtemp())

        if collection:
            self.filepath = self.filepath.joinpath(collection)

        # ensure folder exists
        self.filepath.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"FileAgent will save cache to {self.filepath}")

    def connect(self):
        self.connected = True

    def reset(self):
        from shutil import rmtree

        rmtree(self.filepath)
        self.filepath.mkdir(parents=True, exist_ok=True)

    def read(self, cache_key):
        file_name = self.filepath.joinpath(cache_key)
        if not file_name.exists():
            self.logger.debug(f"cache not exists {file_name}")
            return False, None
        else:
            self.logger.debug(f"reading cache from {file_name}")
            with open(file_name, "rb") as f:
                return True, f.read()

    def write(self, serilized_data, cache_key):
        file_name = self.filepath.joinpath(cache_key)
        self.logger.debug(f"writing cache to {file_name}")
        with open(file_name, "wb") as f:
            f.write(serilized_data)

    def delete(self, cache_key):
        file_name = self.filepath.joinpath(cache_key)
        if os.path.exists(file_name):
            os.remove(file_name)
