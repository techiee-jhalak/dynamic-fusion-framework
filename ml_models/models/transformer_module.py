"""Placeholder for Transformer-based sentiment module."""


class TransformerModule:
    def __init__(self, model_name: str = "bert-base-multilingual-cased"):
        self.model_name = model_name

    def predict(self, texts):
        # return placeholder predictions
        return [0.0 for _ in texts]
