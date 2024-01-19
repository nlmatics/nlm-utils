import json
import logging

from nlm_utils.model_client.connection_pool import connection_pool
from nlm_utils.model_client.nlp_client import NlpClient


class BartClient:
    def __init__(
        self,
        url: str,
    ):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        self.url = url
        self.debug = False
        self.nlp_client = NlpClient(url=url)

    def set_debug_flag(self, debug_flag):
        self.debug = debug_flag

    def call_bart(self, prompts, max_length=120):
        url = f"{self.url}/bart/infer"
        headers = {
            "Accept-Encoding": "gzip, deflate",
            "Accept": "*/*",
            "Content-Type": "application/json",
        }
        req_data = {"prompts": prompts, "max_length": max_length}
        req_data = json.dumps(req_data).encode("utf-8")
        resp = connection_pool.request("POST", url, body=req_data, headers=headers)
        result = json.loads(resp.data)
        return result

    def qa_sum(self, questions, passages, **kwargs):
        prompts = BartClient.get_qa_sum_prompts(questions, passages)
        if self.debug:
            self.logger.info(f"QA Summary Message Prompts are : {prompts}")
        result = self.call_bart(prompts, max_length=1024)
        if self.debug:
            self.logger.info(f"Bart QA Summary Results are : {result}")
        answers = {}
        for idx, (answer, confidence) in enumerate(
            zip(result["outputs"], result["confidences"]),
        ):
            answers[str(idx)] = {
                "text": "" if answer == "unanswerable" else answer,
                "start_probs": confidence,
                "end_probs": confidence,
                "probability": confidence,
            }
        return {"answers": [answers, {}]}

    @staticmethod
    def get_qa_sum_prompts(questions, passages, **kwargs):
        prompts = []
        for question, passage in zip(questions, passages):
            prompt = f"###Task: abstractive_qa \n###Question: {question} \n###Passages:{passage}"
            prompts.append(prompt)
        return prompts
