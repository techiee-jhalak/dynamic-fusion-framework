from sklearn.model_selection import StratifiedKFold
import numpy as np


def run_cv(model_factory, X, y, cv=5, random_state=42):
    skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=random_state)
    scores = []
    for train_idx, test_idx in skf.split(X, y):
        X_train = [X[i] for i in train_idx]
        X_test = [X[i] for i in test_idx]
        y_train = y[train_idx]
        y_test = y[test_idx]
        m = model_factory()
        m.fit(X_train, y_train)
        preds = m.predict(X_test)
        scores.append((y_test, preds))
    return scores
