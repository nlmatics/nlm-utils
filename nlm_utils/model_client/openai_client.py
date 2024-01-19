import logging
import os
import re

import openai

from nlm_utils.utils.answer_type import answer_type_map

DEPLOYMENT_NAME = os.getenv("OPENAI_DEPLOYMENT_NAME", "")


class OpenAIClient:
    def __init__(
        self,
        model: str = "text-davinci-003",
    ):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        self.model = model
        self.debug = False
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

        openai.api_key = os.getenv("OPENAI_API_KEY", "")
        openai.api_base = os.getenv("OPENAI_API_BASE", "")
        openai.api_type = "azure"
        openai.api_version = "2023-05-15"  # this may change in the future

    def set_model(self, model):
        self.model = model

    def set_debug_flag(self, debug_flag):
        self.debug = debug_flag

    def call_open_ai(self, prompts, max_length=120, replace_new_line=True):
        outputs = []
        confidences = []
        for prompt in prompts:
            try:
                response = openai.Completion.create(
                    model=self.model,
                    prompt=prompt,
                    temperature=0.7,
                    max_tokens=max_length,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0,
                )
                output = response.choices[0].text
                if replace_new_line:
                    output = output.replace("\n", "")
            except (
                openai.error.APIError,
                openai.error.APIConnectionError,
                openai.error.Timeout,
                openai.error.RateLimitError,
                openai.error.InvalidRequestError,
                openai.error.ServiceUnavailableError,
            ) as e:
                self.logger.info(f"OpenAI API returned an Error: {str(e)}")
                output = "We are experiencing high volume. Please try again later."

            outputs.append(output)
            confidence = 0.99
            confidences.append(confidence)
        return {"outputs": outputs, "confidences": confidences}

    def call_chat_gpt(self, messages, max_length=120):
        outputs = []
        confidences = []
        for message in messages:
            try:
                response = openai.ChatCompletion.create(
                    engine=DEPLOYMENT_NAME,
                    messages=message,
                    temperature=0.1,
                    max_tokens=max_length,
                    frequency_penalty=0,
                    presence_penalty=0,
                )
                output = (
                    response.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                )
            except (
                openai.error.APIError,
                openai.error.APIConnectionError,
                openai.error.Timeout,
                openai.error.RateLimitError,
                openai.error.InvalidRequestError,
                openai.error.ServiceUnavailableError,
            ) as e:
                self.logger.info(f"OpenAI API returned an Error: {str(e)}")
                output = "We are experiencing high volume. Please try again later."
            # output = output.replace("\n", "")
            outputs.append(output)
            confidence = 0.99
            confidences.append(confidence)
        return {"outputs": outputs, "confidences": confidences}

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
          Extract answer for the following question by reading the passage
          Passage: {passage}
          Question: {question}
        """
            prompt = prompt.replace("\n", "").replace("\t", "")
            prompt = re.sub(r"\s+", " ", prompt)
            prompts.append(prompt)
        return prompts

    @staticmethod
    def get_qa_prompts(questions, sentences):
        prompts = []
        for question, sentence in zip(questions, sentences):
            context = sentence
            # prompt = (
            #     f"Extract an answer to the following question from the following passage:\n"
            #     f"Passage: {conte}\n"
            #     f"Question: {question}\n"
            # )
            # # prompt = f"{context}\n{question}"
            prompt = (
                f"Read this and extract answer for the question. If the question is unanswerable, "
                f'say "unanswerable".\n\nQuestion:{question}?\n\nPassage:{context}'
            )
            prompts.append(prompt)
        return prompts

    @staticmethod
    def get_chat_gpt_answering_prompts(questions, sentences, **kwargs):
        message_prompts = []
        references = kwargs.get("references", [])
        is_summarization = kwargs.get("is_summarization", False)
        system_prompt = (
            "You are an assistant who answers questions based on the context provided."
        )
        user_prompt = (
            "Read the following and answer the question after resolving any references."
        )
        if is_summarization:
            system_prompt = "You are an assistant who answers questions based on the context provided."
            # user_prompt = (
            #     "Read the following and answer the question after resolving any references. "
            #     "Do not mention the word 'passage' while answering."
            # )
            user_prompt = (
                "Write a high-quality abstractive answer for the given question using the provided search "
                "results (some of which might be irrelevant)."
            )
        for question, sentence, reference in zip(questions, sentences, references):
            message_prompt = [
                {
                    "role": "system",
                    "content": f'{system_prompt} If the question is unanswerable, say "unanswerable". '
                    f'Do not mention the word "passage" while answering.',
                },
            ]
            user_message = f"{user_prompt} Question: {question}?\n\nPassage: {sentence}"
            if reference:
                user_message += f"\n\nReferences: {reference}"
            message_prompt.append(
                {
                    "role": "user",
                    "content": user_message,
                },
            )
            message_prompts.append(message_prompt)
        return message_prompts

    @staticmethod
    def get_da_vinci_answering_prompts(questions, sentences, references):
        message_prompts = []
        for question, sentence, reference in zip(questions, sentences, references):
            if reference:
                user_message = (
                    f"Read the following and answer the question after resolving any references. "
                    f"Question:{question}?\n\nPassage: {sentence}"
                )
            else:
                user_message = (
                    f"Read the following and answer the question. "
                    f"Question:{question}?\n\nPassage: {sentence}"
                )
            if reference:
                user_message += f"\n\nReferences: {reference}"
            message_prompts.append(user_message)
        return message_prompts

    @staticmethod
    def get_frame_question_prompts(answers, passages):
        message_prompts = []
        for answer, passage in zip(answers, passages):
            message_prompt = [
                {
                    "role": "system",
                    "content": "You are an assistant who frames questions to retrieve "
                    "the answer based on the context provided.",
                },
            ]
            user_message = (
                f"Frame a question for retrieving the answer {answer} from the following passage. "
                f"\nPassage: {passage}"
            )
            message_prompt.append(
                {
                    "role": "user",
                    "content": user_message,
                },
            )
            message_prompts.append(message_prompt)
        return message_prompts

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

    def get_boolq_prompts(self, questions, sentences):
        prompts = []
        for question, sentence in zip(questions, sentences):
            options_ = "yes or no"
            # prompt = f"{sentence}\n\n{question}?\n\n{options_}"
            prompt = (
                f"Read this and answer the question with {options_}. If the question is unanswerable, "
                f'say "unanswerable".\n\nQuestion:{question}?\n\nPassage:{sentence}'
            )
            prompts.append(prompt)

            prompts.append(prompt)
        return prompts

    def qa_type(self, questions):
        prompts = OpenAIClient.get_qa_type_prompts(questions)
        result = self.call_open_ai(prompts, max_length=20)
        predictions = []
        for pred in result["outputs"]:
            if pred.strip() != "":
                key = pred.split(",")[0].strip().lower()
                if key in answer_type_map:
                    predictions.append(
                        answer_type_map[pred.split(",")[0].strip().lower()],
                    )
                else:
                    predictions.append("Unknown")
            else:
                predictions.append("Unknown")
        return {"predictions": predictions}

    def boolq(self, questions, sentences):
        prompts = self.get_boolq_prompts(questions, sentences)
        result = self.call_open_ai(prompts, max_length=120)
        # look at "outputs" key in result, convert yes to "True" and no to "False" and anything else to "Neutral"
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

        return {"predictions": predictions, "probs": probs}

    def qa(self, questions, sentences):
        print("questions", questions)
        print("sentences", sentences)
        prompts = OpenAIClient.get_qa_prompts(questions, sentences)
        result = self.call_open_ai(prompts, max_length=256)
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

    def qa_sum(self, questions, sentences, **kwargs):
        if self.model == "text-davinci-003":
            message_prompts = OpenAIClient.get_da_vinci_answering_prompts(
                questions,
                sentences,
                kwargs.get("references", []),
            )
            if self.debug:
                self.logger.info(f"Message Prompts are : {message_prompts}")
            result = self.call_open_ai(
                message_prompts,
                max_length=500,
                replace_new_line=False,
            )
        else:
            message_prompts = OpenAIClient.get_chat_gpt_answering_prompts(
                questions,
                sentences,
                **kwargs,
            )
            if self.debug:
                self.logger.info(f"Message Prompts are : {message_prompts}")
            result = self.call_chat_gpt(message_prompts, max_length=512)
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
        if self.debug:
            self.logger.info(f"Open AI Answers: {answers}")
        return {
            "answers": [answers, {}],
        }
