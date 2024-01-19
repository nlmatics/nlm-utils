import numpy as np

from .preprocessing import preprocessor


def calc_BM25_params(block_texts, preprocessor=preprocessor):
    """
    Calculates the internal statistics necessary for BM25 scoring.
    Calculates bm25 during upload time.

    Params:
        block_texts : List[str]

    Returns:
        df, idf, doc_length, avgdl : Tuple(Dict, Dict, np.ndarray, float)
    """
    df = {}
    idf = {}
    n_block_texts = len(block_texts) if block_texts else 1
    doc_length = np.zeros(n_block_texts)
    avgdl = 0
    for index, text in enumerate(block_texts):
        words, cap_words, quote_words = preprocessor(text, get_caps=True)
        doc_length[index] += len(words)
        avgdl += len(words)
        word2freq = {}

        # Get base df
        for word in words:
            word2freq[word] = word2freq.get(word, 0) + 1

        # Get IDF
        for word, _ in word2freq.items():
            idf[word] = idf.get(word, 0) + 1

        # Count quoted words in df
        for word in quote_words:
            word2freq["boost_" + word] = 2

            # If quotes AND capitalized, upweight even more
            if word in cap_words:
                word2freq["boost_" + word] = 4

        # Set df
        df[index] = word2freq
    avgdl /= n_block_texts
    for word, freq in idf.items():
        idf[word] = np.log(n_block_texts / freq)
    return df, idf, doc_length, avgdl
