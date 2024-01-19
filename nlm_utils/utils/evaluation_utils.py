from collections import Counter

from nlm_utils.utils.preprocessing import preprocessor

normalize_answer = preprocessor


def get_tokens(s):
    if not s:
        return []
    return normalize_answer(s)


def score_number(a_gold, a_pred):
    if a_gold.startswith("$") or a_gold.endswith("sf"):
        try:
            num_gold = float(
                a_gold[1:].replace("$", "").replace("sf", "").replace(",", ""),
            )
            num_pred = float(
                a_pred[1:].replace("$", "").replace("sf", "").replace(",", ""),
            )
            return 1 if abs(num_gold / num_pred - 1) < 0.01 else 0
        except Exception:
            pass


def compute_em(a_gold, a_pred):
    score = score_number(a_gold, a_pred)
    if score:
        return score

    return int(normalize_answer(a_gold) == normalize_answer(a_pred))


def compute_f1(a_gold, a_pred):
    score = score_number(a_gold, a_pred)
    if score:
        return score

    gold_toks = get_tokens(a_gold)
    pred_toks = get_tokens(a_pred)
    common = Counter(gold_toks) & Counter(pred_toks)
    num_same = sum(common.values())
    if len(gold_toks) == 0 or len(pred_toks) == 0:
        # If either is no-answer, then F1 is 1 if they agree, 0 otherwise
        return int(gold_toks == pred_toks)
    if num_same == 0:
        return 0
    precision = 1.0 * num_same / len(pred_toks)
    recall = 1.0 * num_same / len(gold_toks)
    f1 = (2 * precision * recall) / (precision + recall)
    return f1


def evaluate_boolq(
    boolq_client,
    boolq_questions,
    boolq_passages,
    truths,
    ids=[],
    threshold=0.8,
):
    def compare_truth_to_pred(truths, preds, probs=[]):
        incorrect_questions = []
        incorrect_passages = []
        incorrect_labels = []
        incorrect_preds = []
        incorrect_ids = []
        incorrect_probs = []
        correct_ids = []
        for idx, (truth, pred) in enumerate(zip(truths, preds)):
            if pred == "True":
                prob = probs[idx][0]
            elif pred == "False":
                prob = probs[idx][2]
            else:
                prob = probs[idx][1]
            if str(truth) != str(pred) or (truth != "Neutral" and prob < threshold):
                print(truth, pred, prob, probs[idx])
                incorrect_questions.append(boolq_questions[idx])
                incorrect_passages.append(boolq_passages[idx])
                incorrect_labels.append(truth)
                incorrect_preds.append(pred)
                incorrect_probs.append(prob)
                if len(ids) > 0:
                    incorrect_ids.append(ids[idx])
            elif len(ids) > 0:
                correct_ids.append(ids[idx])
        # print(str(n_correct) + "/" + str(len(preds)), "accuracy: ", (len(preds) - n_correct)/len(preds))
        accuracy = 0.0
        if len(preds) > 0:
            accuracy = (len(preds) - len(incorrect_labels)) / len(preds)
        return (
            accuracy,
            incorrect_questions,
            incorrect_passages,
            incorrect_preds,
            incorrect_labels,
            incorrect_ids,
            incorrect_probs,
            correct_ids,
        )

    res = boolq_client(
        questions=boolq_questions,
        sentences=boolq_passages,
        return_labels=True,
        return_probs=True,
    )
    return compare_truth_to_pred(truths, res["predictions"], res["probs"])
