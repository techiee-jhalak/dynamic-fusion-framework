import re


TOKEN_RE = re.compile(r"\w+|[^	\w\s]", re.UNICODE)


def simple_tokenize(text: str, lower: bool = True):
    if lower:
        text = text.lower()
    tokens = TOKEN_RE.findall(text)
    return tokens
