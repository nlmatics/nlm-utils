import json
import logging
from timeit import default_timer

from nlm_utils.model_client.connection_pool import connection_pool


def get_iou(bb1, bb2):
    bb1 = {
        "x1": bb1[0],
        "x2": bb1[2],
        "y1": bb1[1],
        "y2": bb1[3],
    }
    bb2 = {
        "x1": bb2[0],
        "x2": bb2[2],
        "y1": bb2[1],
        "y2": bb2[3],
    }

    # print(bb1)
    assert bb1["x1"] <= bb1["x2"]
    assert bb1["y1"] <= bb1["y2"]
    assert bb2["x1"] <= bb2["x2"]
    assert bb2["y1"] <= bb2["y2"]

    x_left = max(bb1["x1"], bb2["x1"])
    y_top = max(bb1["y1"], bb2["y1"])
    x_right = min(bb1["x2"], bb2["x2"])
    y_bottom = min(bb1["y2"], bb2["y2"])

    if x_right < x_left or y_bottom < y_top:
        return 0.0

    intersection_area = (x_right - x_left + 1) * (y_bottom - y_top + 1)

    bb1_area = (bb1["x2"] - bb1["x1"] + 1) * (bb1["y2"] - bb1["y1"] + 1)
    bb2_area = (bb2["x2"] - bb2["x1"] + 1) * (bb2["y2"] - bb2["y1"] + 1)

    iou = intersection_area / float(bb1_area + bb2_area - intersection_area)
    assert iou >= 0.0
    assert iou <= 1.0
    return iou


class YoloClient:
    def __init__(
        self,
        url="http://18.222.177.211",
    ):
        """
        This is a client to interact with the nlp_server
        """

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

        self.connection = connection_pool

        self.url = f"{url}/yolo"

    def __call__(self, doc_id, page_idxs=[]):
        self.logger.info(f"Running YOLO inference with doc_id {doc_id}")
        wall_time = default_timer()

        req_data = {"doc_id": doc_id}
        if page_idxs:
            req_data["page_idxs"] = page_idxs
        # req_data = json.dumps(req_data)

        # # try:
        # resp = requests.post(
        #     self.url,
        #     json=req_data,
        #     headers={
        #         "Accept-Encoding": "gzip, deflate",
        #         "Accept": "*/*",
        #         "Content-Type": "application/json",
        #     },
        # )
        resp = self.connection.request(
            "POST",
            self.url,
            body=json.dumps(req_data),
            headers={
                "Accept-Encoding": "gzip, deflate",
                "Accept": "*/*",
                "Content-Type": "application/json",
            },
        )

        if resp.status == 200:
            results = json.loads(resp.data)
            wall_time = (default_timer() - wall_time) * 1000

            self.logger.info(
                f"Yolo finished on {len(results)} pages. Wall time: {wall_time:.2f}ms",
            )
        else:
            raise RuntimeError(f"Exception when query {self.url}: {resp},")
        # except Exception as e:
        #     self.logger.error(e)
        #     # results = [] * len(texts)
        return results

    def active_learning(self, train_samples):
        self.logger.info(f"Doing active learning on {len(train_samples)} samples")
        wall_time = default_timer()

        req_data = {"active_learn_samples": train_samples}

        resp = self.connection.request(
            "POST",
            self.url,
            body=json.dumps(req_data),
            headers={
                "Accept-Encoding": "gzip, deflate",
                "Accept": "*/*",
                "Content-Type": "application/json",
            },
        )
        if resp.status == 200:
            results = json.loads(resp.data)
            wall_time = (default_timer() - wall_time) * 1000

            self.logger.info(
                f"Yolo finished on {len(results)} pages. Wall time: {wall_time:.2f}ms",
            )
        else:
            raise RuntimeError(f"Exception when query {self.url}: {resp},")

    def get_accuracy(self, test_samples):
        overall_iou = 0

        n_labels, n_detections = 0, 0
        n_pages = 0

        less_predictions, more_predictions = 0, 0

        # do test
        for sample in test_samples:
            page_idxs = []
            page_labels = []

            for page in test_samples[sample]:
                n_pages += 1
                page_idxs.append(page["page_idx"])
                page_labels.append(page["bbox"])

            results = self(sample, page_idxs)

            for result, page_label in zip(results, page_labels):
                # print(result)
                predictions = (
                    result["labels"]["table"] if "table" in result["labels"] else []
                )
                for label in page_label:
                    max_iou = 0
                    for p in predictions:
                        max_iou = max(max_iou, get_iou(label, p))
                    overall_iou += max_iou

                if len(page_label) < len(predictions):
                    more_predictions += 1
                if len(page_label) > len(predictions):
                    less_predictions += 1

                n_labels += len(page_label)
                n_detections += len(predictions)

        all_iou = overall_iou / (n_labels + n_detections)
        labeled_iou = overall_iou / n_labels
        detection_rate_per_page = 1 - (less_predictions + more_predictions) / n_pages
        return {
            "n_pages": n_pages,
            "n_labels": n_labels,
            "n_detections": n_detections,
            "detection_rate_per_page": detection_rate_per_page,
            "extra_pred": more_predictions,
            "less_pred": less_predictions,
            "all_iou": all_iou,
            "labeled_iou": labeled_iou,
        }


# yolo = YoloClient("http://3.144.114.164").
# yolo("doc_id")

# yolo.get_accuracy({
#         "249be245": [
#             {
#                 "page_idx": 6,
#                 "bbox": [[46, 102, 284, 246]],
#                 "block_type": "table",
#             },
#         ]
#     })


# yolo = YoloClient("http://18.224.54.200") # http://18.222.177.211
# yolo.active_learning({
#         "7c120dcc": [
#             {
#                 "page_idx": 8,
#                 "bbox": [[68,468,543,520]],
#                 "block_type": "table",
#             },
#         ]
#     })
