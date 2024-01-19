import json
import logging
import re
from timeit import default_timer
from typing import List

import msgpack
import numpy as np

from nlm_utils.model_client.connection_pool import connection_pool
from nlm_utils.utils import normalize_embeddings

# import http.client
# http.client.HTTPConnection.debuglevel = 1


class EncoderClient:
    def __init__(
        self,
        model: str = "sif",
        url: str = None,
        batch_size: int = None,
        use_msgpack: bool = True,
        normalization=True,
        dummy_number=True,
        lower=True,
        retry=5,
    ):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        self.batch_size = batch_size
        self.use_msgpack = use_msgpack
        self.normalization = normalization
        self.dummy_number = dummy_number
        self.lower = lower
        self.retry = retry
        self.connection = connection_pool
        self.model = model
        self.url = url

        # reg for dummy number
        self.regx = re.compile(
            r"(?<![\d.])(?!\.\.)(?<![\d.][eE][+-])(?<![\d.][eE])(?<!\d[.,])"
            # ---------------------------------
            r"([+-]?)"
            r"(?![\d,]*?\.[\d,]*?\.[\d,]*?)"
            r"(?:0|,(?=0)|(?<!\d),)*"
            r"(?:"
            r"((?:\d(?!\.[1-9])|,(?=\d))+)[.,]?"
            r"|\.(0)"
            r"|((?<!\.)\.\d+?)"
            r"|([\d,]+\.\d+?))"
            r"0*"
            # ---------------------------------
            r"(?:"
            r"([eE][+-]?)(?:0|,(?=0))*"
            r"(?:"
            r"(?!0+(?=\D|\Z))((?:\d(?!\.[1-9])|,(?=\d))+)[.,]?"
            r"|((?<!\.)\.(?!0+(?=\D|\Z))\d+?)"
            r"|([\d,]+\.(?!0+(?=\D|\Z))\d+?))"
            r"0*"
            r")?"
            # ---------------------------------
            r"(?![.,]?\d)",
        )

    def encode(self, sentences: List[str], headers: List[str] = None, **kwargs):
        url = f"{self.url}/{self.model}/encoder"
        wall_time = default_timer()

        # request data
        req_data = {"sentences": self.pre_process_text(sentences)}

        # insert batch_size if needed
        batch_size = kwargs.get("batch_size", False) or self.batch_size
        if batch_size:
            req_data["batch_size"] = batch_size

        # check if use msgpack
        use_msgpack = kwargs.get("use_msgpack", False) or self.use_msgpack
        if use_msgpack:
            req_data["use_msgpack"] = True

        if headers:
            req_data["headers"] = self.pre_process_text(headers)

        req_data = json.dumps(req_data).encode("utf-8")

        for i in range(self.retry):
            try:
                resp = self.connection.request(
                    "POST",
                    url,
                    body=req_data,
                    headers={
                        "Accept-Encoding": "gzip, deflate",
                        "Accept": "*/*",
                        "Content-Type": "application/json",
                    },
                )

                wall_time = (default_timer() - wall_time) * 1000

                self.logger.info(
                    f"{self.__class__.__name__} Encoded {len(sentences)} sentences. Wall time: {wall_time:.2f}ms",
                )

                if resp.status == 200:
                    if use_msgpack:
                        data = msgpack.unpackb(resp.data, raw=False)
                        # unpack embeddings from binary
                        data["embeddings"] = np.frombuffer(
                            data["embeddings"],
                            dtype=np.float32,
                        ).reshape(
                            len(sentences),
                            -1,
                        )
                        # filling nan
                        data["embeddings"] = np.nan_to_num(data["embeddings"])
                    else:
                        data = json.loads(resp.data)

                    if self.normalization:
                        data["embeddings"] = normalize_embeddings(data["embeddings"])
                    else:
                        data["embeddings"] = [
                            [round(y, 8) for y in x]
                            for x in data["embeddings"].tolist()
                        ]
                    return data
                else:
                    raise RuntimeError(f"Exception: {resp.status} from {url}")
            except Exception as e:
                self.logger.error(
                    f"Error in encoder to {self.url}, retried {i} times: {e}",
                    exc_info=True,
                )

    def compare(self, sentences_a: List[str], sentences_b: List[str] = None, **kwargs):
        url = f"{self.url}/{self.model}/similarity"

        wall_time = default_timer()

        # request data
        req_data = {
            "sentences_a": self.pre_process_text(sentences_a),
            "sentences_b": self.pre_process_text(sentences_b),
        }

        # insert batch_size if needed
        batch_size = kwargs.get("batch_size", False) or self.batch_size
        if batch_size:
            req_data["batch_size"] = batch_size

        # check if use msgpack
        use_msgpack = kwargs.get("use_msgpack", False) or self.use_msgpack
        if use_msgpack:
            req_data["use_msgpack"] = True

        req_data = json.dumps(req_data).encode("utf-8")
        for i in range(self.retry):
            try:
                resp = self.connection.request(
                    "POST",
                    url,
                    body=req_data,
                    headers={
                        "Accept-Encoding": "gzip, deflate",
                        "Accept": "*/*",
                        "Content-Type": "application/json",
                    },
                )

                wall_time = (default_timer() - wall_time) * 1000

                self.logger.info(
                    f"{self.__class__.__name__} Compared {len(sentences_a)} with {len(sentences_b)} sentences. Wall time: {wall_time:.2f}ms",
                )

                if resp.status == 200:
                    if use_msgpack:
                        data = msgpack.unpackb(resp.data, raw=False)
                        # unpack sims from binary
                        data["sims"] = np.frombuffer(
                            data["sims"],
                            dtype=np.float32,
                        ).reshape(len(sentences_a), len(sentences_b))
                        # filling nan
                        data = np.nan_to_num(data)
                    else:
                        data = json.loads(resp.data)
                    return data
                else:
                    raise RuntimeError(f"Exception: {resp.text}")
            except Exception as e:
                self.logger.error(
                    f"Error in encoder to {self.url}, retried {i} times: {e}",
                    exc_info=True,
                )

    def __call__(self, sentences_a: List[str], sentences_b: List[str] = None, **kwargs):
        if len(sentences_a) == 0:
            return {"embeddings": []}
        if kwargs.get("compare", False):
            return self.compare(sentences_a, sentences_b, **kwargs)
        else:
            return self.encode(sentences_a, **kwargs)

    def tokenize_numbers(self, sentence):
        def dzs_numbs(x):  # ds = detect and zeros-shave
            if not self.regx.findall(x):
                yield x, x, x
            for mat in self.regx.finditer(x):
                yield (
                    mat.group(),
                    "".join(
                        ("" if n.startswith(".") else "") + "1" if i == 0 else ""
                        for i, n in enumerate(mat.groups(""))
                    ),
                    mat.groups(""),
                )

        tmp = sentence
        for strmatch, modified, _ in dzs_numbs(sentence):
            tmp = tmp.replace(strmatch, modified)
        return tmp

    def pre_process_text(self, texts):
        texts = [x or "" for x in texts]
        if self.lower:
            texts = [x.lower() for x in texts]
        if self.dummy_number:
            texts = [self.tokenize_numbers(x) for x in texts]
        return texts
