import json
import logging
import re

from nlm_utils.model_client.connection_pool import connection_pool
from nlm_utils.model_client.nlp_client import NlpClient
from nlm_utils.utils.answer_type import answer_type_map

# Flan Prompt Reference is available here: https://github.com/google-research/FLAN/blob/main/flan/templates.py


class FlanT5Client:
    def __init__(
        self,
        url: str = None,
    ):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        self.url = url
        self.debug = False
        self.nlp_client = NlpClient(url=url)

    def set_debug_flag(self, debug_flag):
        self.debug = debug_flag

    def call_flan_t5(self, prompts, max_length=120):
        url = f"{self.url}/flan-t5/infer"
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

    def qa_type(self, questions):
        prompts = FlanT5Client.get_qa_type_prompts(questions)
        result = self.call_flan_t5(prompts, max_length=20)
        predictions = []
        for pred in result["outputs"]:
            if pred.strip() != "":
                predictions.append(answer_type_map[pred.split(",")[0].strip()])
            else:
                predictions.append("Unknown")
        return {"predictions": predictions}

    def boolq(self, questions, sentences, **kwargs):
        prompts = FlanT5Client.get_boolq_prompts(questions, sentences, **kwargs)
        if self.debug:
            self.logger.info(f"BOOLQ Message Prompts are : {prompts}")
        result = self.call_flan_t5(prompts, max_length=500)
        if self.debug:
            self.logger.info(f"FlanT5Client BOOLQ Results are : {result}")
            # look at "outputs" key in result, convert yes to "True" and no to "False" and anything else to "Neutral"
        if not kwargs.get("is_summarization", False):
            predictions = []
            for pred in result["outputs"]:
                if pred == "yes":
                    pred = "True"
                elif pred == "no":
                    pred = "False"
                else:
                    pred = "Neutral"
                predictions.append(pred)
            #  turn result["confidences"] into a list of one item arrays
            probs = [[confidence] for confidence in result["confidences"]]
            output = {"predictions": predictions, "probs": probs}
        else:
            answers = {}
            for idx, (answer, confidence) in enumerate(
                zip(result["outputs"], result["confidences"]),
            ):
                if answer == "yes":
                    answer = "Yes"
                elif answer == "no":
                    answer = "No"
                else:
                    answer = "Neutral"
                answers[str(idx)] = {
                    "text": answer,
                    "start_probs": confidence,
                    "end_probs": confidence,
                    "probability": confidence,
                }

            output = {"answers": [answers, {}]}
        return output

    def qa(self, questions, sentences, **kwargs):
        prompts = FlanT5Client.get_qa_prompts(questions, sentences, **kwargs)
        if self.debug:
            self.logger.info(f"QA Message Prompts are : {prompts}")
        result = self.call_flan_t5(prompts, max_length=500)
        if self.debug:
            self.logger.info(f"FlanT5Client QA Results are : {result}")
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

    def get_mnli_prompts(self, questions, sentences):
        prompts = []
        # get unique questions
        uniq_questions = list(set(questions))
        uniq_hypotheses = self.nlp_client(
            texts=uniq_questions,
            option="convert_question_to_sentence",
        )
        # create map with key as question and value as hypothesis
        question_hypothesis_map = dict(zip(uniq_questions, uniq_hypotheses))
        hypotheses = []
        for question in questions:
            hypotheses.append(question_hypothesis_map[question])

        for hypothesis, sentence in zip(hypotheses, sentences):
            premise = sentence
            options_ = ""
            prompt = (
                f"Premise: {premise}\n\nHypothesis: {hypothesis}\n\n"
                f"Does the premise entail the hypothesis?\n\n{options_}"
            )
            prompts.append(prompt)
        return prompts

    @staticmethod
    def get_qa_type_prompts(questions):
        prompts = []
        for question in questions:
            #         question = "what is effective for oral cancer"
            prompt = f"""
            What type of answer does the following question expect:
            {question}
            Options: state, city, country, location, mountain, work of art,
            currency, event, product, food, disease, body, substance, sport,
            equivalent term, vehicle, technology or method, color, religion,
            language, money, date, period, count, code, volume or size, distance,
            temperature, weight, percent, speed, description, definition, reason,
            person, organization, gene, mutation, cell line, cell type, dna, rna, drug, yes/no
            """
            prompt = prompt.replace("\n", "").replace("\t", "")
            prompt = re.sub(r"\s+", " ", prompt)
            prompts.append(prompt.strip())
        return prompts

    @staticmethod
    def get_qa2_prompts(questions, sentences):
        prompts = []
        for question, sentence in zip(questions, sentences):
            passage = sentence
            prompt = f"""
          answer the following question by reading the passage
          Passage: {passage}
          Question: {question}
        """
            prompt = prompt.replace("\n", "").replace("\t", "")
            prompt = re.sub(r"\s+", " ", prompt)
            prompts.append(prompt)
        return prompts

    @staticmethod
    def get_qa_prompts(questions, sentences, **kwargs):
        prompts = []
        for question, sentence in zip(questions, sentences):
            # prompt = f'{context}\n{question} (If the question is unanswerable, say "unanswerable")'
            # prompt = f'Read this and answer the question. If the question is unanswerable, say "unanswerable".' \
            #          f'\n\n{context}\n\n{question}'
            prompt = (
                f"Read the following and answer the question after resolving any references. "
                f"Question: {question}?\n\nPassage: {sentence}"
            )
            summary_prompt_template = kwargs.get("summary_qa_prompt_template", "")
            if summary_prompt_template:
                prompt = summary_prompt_template.format(
                    sentence=sentence,
                    question=question,
                )
            prompts.append(prompt)
        return prompts

    @staticmethod
    def get_boolq_prompts(questions, sentences, **kwargs):
        prompts = []
        for question, sentence in zip(questions, sentences):
            options_ = ""
            prompt = f'{sentence}\n\n{question}?If the question is unanswerable, say "unanswerable".\n\n{options_}'
            summary_prompt_template = kwargs.get("summary_boolq_prompt_template", "")
            if summary_prompt_template:
                prompt = summary_prompt_template.format(
                    sentence=sentence,
                    question=question,
                    options_=options_,
                )
            prompts.append(prompt)
        return prompts
