import logging
import pickle
from dataclasses import is_dataclass  # noreorder
from functools import wraps

from xxhash import xxh64

from .file_agent import FileAgent
from .memory_agent import MemoryAgent
from .mongodb_agent import MongodbAgent
from .redis_agent import RedisAgent

from timeit import default_timer

FS_AGENTS = {
    "FileAgent": FileAgent,
    "MemoryAgent": MemoryAgent,
    "RedisAgent": RedisAgent,
    "MongodbAgent": MongodbAgent,
    "File": FileAgent,
    "Memory": MemoryAgent,
    "Redis": RedisAgent,
    "Mongodb": MongodbAgent,
}


class Cache:
    __name__ = "Cache"

    def __init__(
        self,
        fs_agent,
        protocol="pickle",
        grpc_object=None,
        *args,
        **kwargs,
    ):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)
        self.protocol = protocol.lower()
        self.grpc_object = grpc_object
        if self.protocol == "grpc" and self.grpc_object is None:
            raise ValueError("Please set grpc_object when using grpc protocol")

        if isinstance(fs_agent, str):
            self.fs_agent = FS_AGENTS[fs_agent](*args, **kwargs)
        else:
            self.fs_agent = fs_agent

        # connect fs_agent
        self.fs_agent.connect()
        if self.connected:
            self.logger.info(
                f"Cache is initialized with client: {self.fs_agent.__name__}",
            )
        else:
            self.logger.info(
                f"Cache is not connected to {self.fs_agent.__name__}, skipping cache.",
            )

    @property
    def connected(self):
        return self.fs_agent.connected

    def __call__(self, func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            # remove reserved_kwarg before going into func
            f_kwargs = kwargs.copy()
            for reserved_kwarg in ["overwrite", "cache_key", "no_cache"]:
                if reserved_kwarg in f_kwargs:
                    del f_kwargs[reserved_kwarg]

            wall_time = default_timer()

            # agent not connected
            if not self.connected:
                self.logger.error("Cache Agent is not connected. Skiping the cache.")
                return func(*args, **f_kwargs)

            # no_cache passed, skiping
            if kwargs.get("no_cache", False):
                self.logger.error("`no_cache` is set to True. Skiping the cache.")
                return func(*args, **f_kwargs)

            # function mush have args or kwargs to be cached
            if not args and not kwargs:
                self.logger.warning(
                    f"Can not apply cache to function {func} : both args and kwargs are empty",
                )

            # read cache and cache_key
            status, data, cache_key = self.read_cache(func, *args, **kwargs)
            if status and data is not None:
                self.logger.info(
                    f"reading cache: key='{cache_key}' in {default_timer() - wall_time:.4f}s",
                )
                return data

            # cache not found
            self.logger.info(f"generating cache: key='{cache_key}'")

            # run function to get cache
            data = func(*args, **f_kwargs)

            if data is not None:
                # write serilized_data to agent
                self.write_cache(data, cache_key)

            self.logger.info(
                f"saving cache: key='{cache_key}' in {default_timer() - wall_time:.4f}s",
            )
            return data

        return wrapped

    def get_cache_key(self, *args, **kwargs):
        # use pickle to dump binary context of python object
        # pickle is in memory operations.
        # tested with a 300,000 words doc.
        # It takes 11.5 µs to generate the binary
        # hash should take both args and kwargs so that cache is assosicated
        # with both data and hyper-parameters
        if "cache_key" in kwargs:
            return kwargs["cache_key"]
        if "overwrite" in kwargs:
            del kwargs["overwrite"]

        self.logger.info("no cache_key provided, generating by hashing")
        hash_args = []
        # remove class object from args
        for index, arg in enumerate(args):
            # convert the argument if it is not builtin types
            if arg.__class__.__module__ != "builtins":
                # use uid for dataclass if provided
                if is_dataclass(arg) and hasattr(arg, "uid"):
                    arg = arg.uid
                # use class name for other cases
                else:
                    arg = arg.__class__.__name__
            hash_args.append(arg)

        # dump to highest protocal to generate unique id
        data = pickle.dumps((hash_args, kwargs), protocol=-1)

        # hash with xxh64
        cache_key = xxh64(data).hexdigest()
        return cache_key

    def read_cache(self, func, *args, **kwargs):
        # get cache_key
        cache_key = self.get_cache_key(func.__name__, *args, **kwargs)
        status = False

        # check if overwrite
        if kwargs.get("overwrite", False):
            self.logger.info(f"overwriting cache: key='{cache_key}'")
            return status, None, cache_key

        # read cache
        status, serilized_data = self.fs_agent.read(cache_key)

        data = None
        if status:
            # deserilize object
            try:
                # deserilize pickle
                if self.protocol == "pickle":
                    data = pickle.loads(serilized_data)
                # deserilize grpc
                elif self.protocol == "grpc":
                    data = self.grpc_object.FromString(serilized_data)
                # return original data
                else:
                    data = serilized_data
            except Exception as e:
                self.logger.error(f"unable to read cache key='{cache_key}', {e}")
                status = False
        else:
            self.logger.info(f"cache key='{cache_key}' not found, skipping")

        return status, data, cache_key

    def write_cache(self, data, cache_key):
        if self.connected:

            # serilize data
            if self.protocol == "pickle":
                # pickle object with protocol 4
                serilized_data = pickle.dumps(data, protocol=4)
            elif self.protocol == "grpc":
                # serilize to protobuf
                serilized_data = data.SerializeToString()
            else:
                serilized_data = data
                assert isinstance(serilized_data, [str, bytes])

            self.fs_agent.write(serilized_data, cache_key)

    def delete_cache(self, cache_key):
        if self.connected:
            self.fs_agent.delete(cache_key)

    def reset(self):
        if self.connected:
            self.fs_agent.reset()
