from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import numpy as np


class TransformerWrapper:
    def __init__(self, model_name: str):
        self.model_name = model_name
        try:
            self.pipe = pipeline('sentiment-analysis', model=model_name, tokenizer=model_name)
        except Exception:
            self.pipe = None

    def predict_proba(self, texts):
        # returns Nx2 probabilities if pipeline available, else zeros
        if self.pipe is None:
            return np.zeros((len(texts), 2))
        out = self.pipe(texts, truncation=True)
        probs = []
        for o in out:
            # some pipelines return label and score
            label = o.get('label')
            score = o.get('score', 0.0)
            if label and label.lower().startswith('neg'):
                probs.append([score, 1 - score])
            else:
                probs.append([1 - score, score])
        return np.array(probs)

    def predict(self, texts):
        probs = self.predict_proba(texts)
        return probs.argmax(axis=1)
