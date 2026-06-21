from research_pipeline.src.preprocessing.tokenizer import simple_tokenize
from research_pipeline.src.stats.text_stats import text_statistics


def test_tokenizer_basic():
    toks = simple_tokenize("Hello, world!")
    assert 'Hello' in ' '.join(toks) or 'hello' in ' '.join(toks)


def test_text_stats_returns_keys():
    s = text_statistics("hi :) soooo नमस्ते")
    for k in ['token_count','emoji_count','repeated_tokens','symbol_count','non_english_tokens']:
        assert k in s
