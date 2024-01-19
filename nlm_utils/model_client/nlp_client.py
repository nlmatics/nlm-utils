import json
import logging
from timeit import default_timer
from typing import List

from nlm_utils.model_client.connection_pool import connection_pool


class NlpClient:
    def __init__(
        self,
        url: str = None,
        model: str = "nlp",
    ):
        """
        This is a client to interact with the nlp_server
        """

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

        self.connection = connection_pool

        self.url = f"{url}/{model}"

    # @cache
    def __call__(self, texts: List[str], option: str, domain: str = "", **kwargs):
        self.logger.info(f"Running NLP server with option {option}.. domain {domain}")
        wall_time = default_timer()

        req_data = {
            "option": option,
            "texts": texts,
        }
        if domain:
            req_data["domain"] = domain
        req_data = json.dumps(req_data).encode("utf-8")

        try:
            resp = self.connection.request(
                "POST",
                self.url,
                body=req_data,
                headers={
                    "Accept-Encoding": "gzip, deflate",
                    "Accept": "*/*",
                    "Content-Type": "application/json",
                },
            )

            if resp.status == 200:
                results = json.loads(resp.data)["data"]
                wall_time = (default_timer() - wall_time) * 1000

                self.logger.info(
                    f"Extracting Entities for {len(results)} lines. Wall time: {wall_time:.2f}ms",
                )
            else:
                raise RuntimeError(f"Exception when query {self.url}: {resp.text},")
        except Exception as e:
            self.logger.error(e)
            results = [] * len(texts)

        return results
