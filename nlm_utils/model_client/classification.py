import json
import logging
from typing import List

import msgpack
import numpy as np

from nlm_utils.model_client.bart_client import BartClient
from nlm_utils.model_client.connection_pool import connection_pool
from nlm_utils.model_client.flan_t5_client import FlanT5Client
from nlm_utils.model_client.openai_client import OpenAIClient


def fix_answer_tokenization_issues(answer):
    answer = answer.strip()
    while len(answer) > 1 and answer[-1] in [
        ",",
        ":",
        ";",
        "(",
    ]:
        answer = answer[0:-1]
    if (
        len(answer) > 1
        and answer[-1] == "."
        and not (answer[0].isupper() or answer[0].isdigit())
    ):
        answer = answer[0:-1]
    if answer[0] in ["("] and ")" not in answer:
        answer = answer[1:]
    return answer


def fix_tokenizer_issues(response):
    if "answers" in response and len(response["answers"]) > 0:
        for a in response["answers"][0].values():
            if a.get("text", ""):
                a["text"] = fix_answer_tokenization_issues(a["text"])


class ClassificationClient:
    def __init__(
        self,
        model: str = "roberta",
        task: str = "qnli",
        url: str = None,
        batch_size: int = None,
        use_msgpack: bool = False,
        retry: int = 5,
        **kwargs,
    ):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        self.model = model
        self.task = task
        self.batch_size = batch_size
        self.use_msgpack = use_msgpack
        self.retry = retry
        self.connection = connection_pool

        self.url = f"{url}/{model}/{task}"
        if self.model in ["flan-t5", "openai", "bart"]:
            self.url = url
        self.model_client = None
        if self.model == "flan-t5":
            self.model_client = FlanT5Client(self.url)
            self.model_client.set_debug_flag(kwargs.get("debug", False))
        elif self.model == "openai":
            self.model_client = OpenAIClient()
            openai_model = kwargs.get("openai_model", "")
            if openai_model:
                self.model_client.set_model(openai_model)
            self.model_client.set_debug_flag(kwargs.get("debug", False))
        elif self.model == "bart":
            self.model_client = BartClient(self.url)
            self.model_client.set_debug_flag(kwargs.get("debug", False))

    # @cache
    def __call__(
        self,
        questions: List[str],
        sentences: List[str] = None,
        return_labels=True,
        return_logits=False,
        return_probs=False,
        **kwargs,
    ):
        if self.model == "flan-t5" and self.model_client:
            if self.task in {"qa", "roberta-qa"}:
                return self.model_client.qa(questions, sentences, **kwargs)
            elif self.task in {"boolq"}:
                return self.model_client.boolq(questions, sentences, **kwargs)
            elif self.task in {"qa_type"}:
                return self.model_client.qa_type(questions)
        elif self.model == "bart" and self.model_client:
            if self.task in {"qa_sum"}:
                return self.model_client.qa_sum(questions, sentences, **kwargs)
        elif self.model == "openai" and self.model_client:
            if self.task in {"qa", "roberta-qa"}:
                return self.model_client.qa(questions, sentences)
            elif self.task in {"boolq"}:
                return self.model_client.boolq(questions, sentences)
            elif self.task in {"qa_type"}:
                return self.model_client.qa_type(questions)
            elif self.task == "qa_sum":
                return self.model_client.qa_sum(questions, sentences, **kwargs)
        else:
            if self.task in {"qa", "phraseqa", "calc"}:
                req_data = {
                    # replace ” with "
                    "questions": questions,
                    "sentences": sentences,
                    "return_logits": return_logits,
                    "return_probs": return_probs,
                }
            elif self.task in {"roberta-qa", "roberta-phraseqa", "roberta-calc"}:
                sentences = [s + "<s>" for s in sentences]
                req_data = {
                    # replace ” with "
                    "left_sentences": sentences,
                    "right_sentences": questions,
                    "return_logits": return_logits,
                    "return_probs": return_probs,
                }
            elif self.task in {"io-qa"}:
                req_data = {
                    "left_sentences": questions,
                    "right_sentences": sentences,
                    "return_logits": return_logits,
                    "return_probs": return_probs,
                }
            else:
                if sentences:
                    req_data = {
                        "left_sentences": questions,
                        "right_sentences": sentences,
                        "return_labels": return_labels,
                        "return_logits": return_logits,
                        "return_probs": return_probs,
                        "keep_statement": kwargs.get("keep_statement", False),
                    }
                else:
                    req_data = {
                        "left_sentences": questions,
                        "return_labels": return_labels,
                        "return_logits": return_logits,
                        "return_probs": return_probs,
                    }

            batch_size = kwargs.get("batch_size", False) or self.batch_size

            if batch_size:
                req_data["batch_size"] = batch_size

            use_msgpack = kwargs.get("use_msgpack", False) or self.use_msgpack

            if use_msgpack:
                req_data["use_msgpack"] = True

            req_data = json.dumps(req_data).encode("utf-8")

            for i in range(self.retry):
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
                        response = None
                        if use_msgpack:
                            data = msgpack.unpackb(resp.data, raw=False)
                            data["predictions"] = np.frombuffer(data["predictions"])
                            response = data
                        else:
                            response = json.loads(resp.data)
                        if self.task in "roberta-qa":
                            fix_tokenizer_issues(response)
                        return response
                    else:
                        raise RuntimeError(
                            f"Exception when query {self.url}: {resp.text},",
                        )
                except Exception as e:
                    self.logger.error(
                        f"Error in classification, retried {i} times: {e}",
                    )

    def active_learning(self, update_workers: bool = False, **req_data):
        req_data.update(
            {
                "update_workers": update_workers,
            },
        )
        req_data.update(
            {
                "restart_workers": True,
            },
        )
        req_data = json.dumps(req_data).encode("utf-8")

        for i in range(self.retry):
            try:
                resp = self.connection.request(
                    "PUT",
                    self.url,
                    body=req_data,
                    headers={
                        "Accept-Encoding": "gzip, deflate",
                        "Accept": "*/*",
                        "Content-Type": "application/json",
                    },
                    retries=False,
                )

                if resp.status == 200:
                    return json.loads(resp.data)
                else:
                    raise RuntimeError(f"Exception when query {self.url}: {resp},")
            except Exception as e:
                self.logger.error(f"Error in classification, retried {i} times: {e}")

    def restart(self, restart_checkpoint: str = ""):
        req_data = {
            "restart_workers": True,
        }
        if restart_checkpoint:
            req_data["restart_checkpoint"] = restart_checkpoint

        req_data = json.dumps(req_data).encode("utf-8")

        try:
            resp = self.connection.request(
                "PUT",
                self.url,
                body=req_data,
                headers={
                    "Accept-Encoding": "gzip, deflate",
                    "Accept": "*/*",
                    "Content-Type": "application/json",
                },
                retries=False,
            )

            if resp.status == 200:
                return json.loads(resp.data)
            else:
                raise RuntimeError(f"Exception in restart {self.url}: {resp},")
        except Exception as e:
            self.logger.error(f"Error in restart  {e}")
