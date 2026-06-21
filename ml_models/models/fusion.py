"""Fusion layer combining lexicon and transformer signals."""


def fuse(lexicon_scores, transformer_scores, alpha=0.5):
    # simple linear fusion placeholder
    return [alpha * l + (1 - alpha) * t for l, t in zip(lexicon_scores, transformer_scores)]
