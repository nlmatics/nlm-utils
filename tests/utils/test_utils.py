import numpy as np

from nlm_utils.utils import normalize_embeddings


def test_normalize_embeddings():
    for a in [
        np.random.rand(3, 10),
        np.random.rand(1, 10),
        [1.0, 2.0, 3.0],
        [],
        [
            [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
        ],
    ]:

        normalize_embeddings(a)


def test_correct_normalization():
    assert np.allclose(normalize_embeddings([0.0, 0.0, 0.0]), [0.0, 0.0, 0.0])
    assert np.allclose(normalize_embeddings([2.0, 0.0, 0.0]), [1.0, 0.0, 0.0])
    assert np.allclose(
        normalize_embeddings([0.0, 1.0, 1.0]),
        [0.0, 1.0 / np.sqrt(2.0), 1.0 / np.sqrt(2.0)],
    )


test_normalize_embeddings()
test_correct_normalization()
