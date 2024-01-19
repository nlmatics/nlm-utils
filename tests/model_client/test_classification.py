import os

from nlm_utils.model_client import ClassificationClient


URL = os.getenv("MODEL_SERVER_URL")


class TestClassification:
    def test_classification_client_qnli(self):
        text_a = [
            "what is the project name?",
        ]
        text_b = [
            "Among these projects was New York City’s 7.5 million square foot World Financial Center.",
        ]
        task = "qnli"
        for model in ["roberta"]:
            client = ClassificationClient(model, task, URL)
            response = client(text_a, text_b)
            print(model, task, response)

    def test_classification_client_squad2(self):
        text_a = [
            "what is the project name?",
        ]
        text_b = [
            "Among these projects was New York City’s 7.5 million square foot World Financial Center.",
        ]
        task = "roberta-qa"
        for model in ["roberta"]:
            client = ClassificationClient(model, task, URL)
            response = client(text_a, text_b)
            print(model, task, response)

    def test_classification_boolq(self):
        text_a = [
            "what is the project name?",
        ]
        text_b = [
            "Among these projects was New York City’s 7.5 million square foot World Financial Center.",
        ]
        task = "boolq"
        for model in ["roberta"]:
            client = ClassificationClient(model, task, URL)
            response = client(text_a, text_b)
            print(model, task, response)
