import re
from collections import Counter
from research_pipeline.src.preprocessing.tokenizer import simple_tokenize
import emoji
from langdetect import detect_langs


REPEATED_CHAR_RE = re.compile(r"(.)\1{2,}")
SYMBOL_RE = re.compile(r"[^\w\s]", re.UNICODE)
DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")


def is_non_english_token(token: str) -> bool:
    # Heuristic: presence of Devanagari or other non-latin script
    if DEVANAGARI_RE.search(token):
        return True
    # otherwise use langdetect fallback for longer tokens
    try:
        if len(token) > 1:
            langs = detect_langs(token)
            if langs and langs[0].prob > 0.8:
                return langs[0].lang != 'en'
    except Exception:
        pass
    return False


def text_statistics(text: str, lower: bool = True) -> dict:
    text = text or ""
    tokens = simple_tokenize(text, lower=lower)
    token_count = len(tokens) or 1
    char_count = len(text)
    emoji_count = sum(1 for ch in text if ch in emoji.EMOJI_DATA)
    repeated_tokens = sum(1 for t in tokens if REPEATED_CHAR_RE.search(t))
    symbol_count = len(SYMBOL_RE.findall(text))
    non_english_tokens = sum(1 for t in tokens if is_non_english_token(t))

    return {
        'token_count': token_count,
        'char_count': char_count,
        'emoji_count': emoji_count,
        'repeated_tokens': repeated_tokens,
        'symbol_count': symbol_count,
        'non_english_tokens': non_english_tokens,
    }
