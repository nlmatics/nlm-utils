import numpy as np

from nlm_utils.utils import calc_BM25_params

test_text = [
    "This is a sentence",
    "This is another such sentence",
    "Here is a third sentence for good measure",
]


def no_preprocessor(s, get_caps=False):
    if get_caps:
        return s.split(" "), [], []
    return s.split(" ")


class TestBM25Params:
    def test_df(self):
        df, _, _, _ = calc_BM25_params(test_text, no_preprocessor)
        assert df[0]["This"] == 1
        assert df[1]["is"] == 1
        assert df[2]["good"] == 1

    def test_idf(self):
        _, idf, _, _ = calc_BM25_params(test_text, no_preprocessor)
        assert idf["This"] == np.log(3 / 2)
        assert idf["is"] == np.log(3 / 3)
        assert idf["good"] == np.log(3 / 1)

    def test_doc_length(self):
        _, _, doc_length, avgdl = calc_BM25_params(test_text, no_preprocessor)
        assert (doc_length == np.array([4.0, 5.0, 8.0])).all()
        assert abs(avgdl - (4 + 5 + 8) / 3) < 1e-5
