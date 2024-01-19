import sys
from functools import lru_cache

import nltk

if sys.version_info[0] >= 3:
    unicode = str

# stemmer = nltk.PorterStemmer().stem
stemmer = nltk.SnowballStemmer("english").stem


tokenizer = nltk.tokenize.RegexpTokenizer(r"\b[a-zA-Z0-9]+\b").tokenize

# Get all-caps words (except one-letter words like "I")
capword_tokenizer = nltk.tokenize.RegexpTokenizer(r"\b[A-Z]{2,}\b").tokenize

# Quote tokenizers
quote_tokenizer = nltk.tokenize.RegexpTokenizer(r'"(.*?)"').tokenize
unicode_quote_tokenizer = nltk.tokenize.RegexpTokenizer(
    "(?:\u201c(.*?)\u201d)",
).tokenize

# tokenizer = nltk.wordpunct_tokenize
# tokenizer = nltk.word_tokenize

STOPWORDS = {
    "i",
    "me",
    "my",
    "myself",
    "we",
    "our",
    "ours",
    "ourselves",
    "you",
    "your",
    "yours",
    "yourself",
    "yourselves",
    "he",
    "him",
    "his",
    "himself",
    "she",
    "her",
    "hers",
    "herself",
    "it",
    "its",
    "itself",
    "they",
    "them",
    "their",
    "theirs",
    "themselves",
    "what",
    "which",
    "who",
    "whom",
    "this",
    "that",
    "these",
    "those",
    "am",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "having",
    "do",
    "does",
    "did",
    "doing",
    "a",
    "an",
    "the",
    "and",
    "but",
    "if",
    "or",
    "because",
    "as",
    "until",
    "while",
    "of",
    "at",
    "by",
    "for",
    "with",
    "about",
    "against",
    "between",
    "into",
    "through",
    "during",
    "before",
    "after",
    "above",
    "below",
    "to",
    "from",
    "up",
    "down",
    "in",
    "out",
    "on",
    "off",
    "over",
    "under",
    "again",
    "further",
    "then",
    "once",
    "here",
    "there",
    "when",
    "where",
    "why",
    "how",
    "all",
    "any",
    "both",
    "each",
    "few",
    "more",
    "most",
    "other",
    "some",
    "such",
    "no",
    "nor",
    "not",
    "only",
    "own",
    "same",
    "so",
    "than",
    "too",
    "very",
    "u",
    "s",
    "t",
    "can",
    "will",
    "just",
    "don",
    "should",
    "now",
}


punctuations = [
    ".",
    "?",
    "!",
]


@lru_cache(maxsize=1024)
def preprocessor(text, get_caps=False, use_stemmer=False):
    """
    get_caps (boolean): Returns stemmed & lowercase list of originally capitalized words
    in addition to original tokens. Right now also gets quoted words.
    """
    if not isinstance(text, unicode):
        text = unicode(text, "utf8", errors="strict")

    for punctuation in punctuations:
        if text.endswith(punctuation):
            text = text[:-1]

    tokens = []

    for token in tokenizer(text.lower()):
        if token in STOPWORDS:
            continue
        if use_stemmer:
            tokens.append(stemmer(token))
        else:
            tokens.append(token)

    if not get_caps:
        return tokens

    # Get capitalized words too
    else:
        cap_tokens = []
        quote_tokens = []

        for token in capword_tokenizer(text):
            if token in STOPWORDS:
                continue
            cap_tokens.append(stemmer(token))

        for token in quote_tokenizer(text):
            if token in STOPWORDS:
                continue
            quote_tokens.append(stemmer(token))

        for token in unicode_quote_tokenizer(text):
            if token in STOPWORDS:
                continue
            quote_tokens.append(stemmer(token))

        return tokens, cap_tokens, quote_tokens


if __name__ == "__main__":
    x = preprocessor("what is the total acquisition cost above 20%?")
    print(x)
