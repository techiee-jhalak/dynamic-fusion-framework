from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import numpy as np


class VaderWrapper:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    def predict_proba(self, texts):
        # return probability-like scores for positive class
        scores = []
        for t in texts:
            c = self.analyzer.polarity_scores(str(t))
            # compound in [-1,1] -> map to [0,1]
            p = (c['compound'] + 1) / 2
            scores.append([1 - p, p])
        return np.array(scores)

    def predict(self, texts, threshold=0.5):
        probs = self.predict_proba(texts)[:,1]
        return (probs >= threshold).astype(int)
