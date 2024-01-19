import numpy as np
import tiktoken

oai_tokenizer = tiktoken.get_encoding(
    "cl100k_base",
)


def normalize_embeddings(X):
    # convert list to numpy
    if isinstance(X, list):
        if not X:
            return X
        X = np.array(X)

    # check dimension
    is_1_dim = X.ndim == 1
    if is_1_dim:
        X = X.reshape(1, -1)

    # normalize
    if len(X):
        norms = np.einsum("ij,ij->i", X, X)
        norms = np.sqrt(norms)
        # add epsilon to avoid division by 0
        X /= norms[:, np.newaxis] + 1e-10
    if is_1_dim:
        return [round(x, 8) for x in X[0].tolist()]
    else:
        return [[round(y, 8) for y in x] for x in X.tolist()]


def ensure_bool(value):
    if isinstance(value, bool):
        return value
    elif isinstance(value, str):
        value = value.lower()
        if value in ("true", "false"):
            return value == "true"
        elif value.isdigit():
            return value != "0"
    raise ValueError(f"Can not cast {type(value)}:'{value}' to boolean")


def ensure_float(value):
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"Can not cast {type(value)}:'{value}' to float")


def ensure_integer(value):
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Can not cast {type(value)}:'{value}' to integer")


def num_tokens_from_string(string: str) -> int:
    """Returns the number of tokens in a text string."""
    num_tokens = len(oai_tokenizer.encode(string))
    return num_tokens