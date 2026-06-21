"""Placeholder for lexicon-based sentiment module."""


class LexiconModule:
    def __init__(self, lexicon_path: str = None):
        self.lexicon_path = lexicon_path

    def score(self, tokens):
        # return lexicon-based scores for tokens
        return [0.0 for _ in tokens]
