from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


def build_logistic_pipeline(**kwargs):
    vec = TfidfVectorizer(max_features=20000)
    clf = LogisticRegression(max_iter=1000)
    pipe = Pipeline([('tfidf', vec), ('clf', clf)])
    return pipe
