import logging
from abc import ABCMeta
from abc import abstractmethod


class BaseAgent(metaclass=ABCMeta):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)
        self.connected = False

    @abstractmethod
    def connect(self):
        NotImplementedError

    @abstractmethod
    def read(self, cache_key):
        NotImplementedError

    @abstractmethod
    def write(self, data, cache_key):
        NotImplementedError

    @abstractmethod
    def delete(self, cache_key):
        NotImplementedError

    @abstractmethod
    def reset(self):
        NotImplementedError
