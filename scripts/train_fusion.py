import json
from pathlib import Path
import os
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in os.sys.path:
    os.sys.path.insert(0, str(ROOT))


def train_and_save(input_path: Path, output_dir: Path, model_path: Path):
    df = pd.read_csv(input_path)
    if 'label' not in df.columns and 'sentiment' in df.columns:
        df['label'] = df['sentiment'].map({'positive': 2, 'negative': 0, 'neutral': 1}).astype(int)

    X = df['text'].astype(str).tolist()
    y = df['label'].astype(int).to_numpy()

    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=4000)),
        ('clf', LogisticRegression(max_iter=4000, solver='lbfgs')),
    ])

    search = GridSearchCV(
        pipeline,
        param_grid={
            'clf__C': [0.5, 1.0, 2.0],
            'clf__class_weight': [None, 'balanced'],
        },
        scoring='f1_macro',
        cv=3,
        n_jobs=-1,
    )
    search.fit(X, y)

    y_pred = search.best_estimator_.predict(X)
    metrics = {
        'accuracy': float(accuracy_score(y, y_pred)),
        'macro_f1': float(f1_score(y, y_pred, average='macro')),
        'best_params': search.best_params_,
        'classes': [int(v) for v in search.classes_],
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    artifact = {
        'pipeline': search.best_estimator_,
        'metrics': metrics,
        'model_type': 'tfidf-logistic-regression',
    }
    joblib.dump(artifact, model_path)

    with open(output_dir / 'training_metrics.json', 'w', encoding='utf-8') as handle:
        json.dump(metrics, handle, indent=2)

    df_metrics = pd.DataFrame([metrics])
    df_metrics.to_csv(output_dir / 'training_metrics.csv', index=False)
    return metrics


if __name__ == '__main__':
    input_path = ROOT / 'data' / 'sail_cleaned.csv'
    output_dir = ROOT / 'research_pipeline' / 'outputs'
    model_path = ROOT / 'ml_models' / 'sail_fusion_model.joblib'
    metrics = train_and_save(input_path, output_dir, model_path)
    print(json.dumps(metrics, indent=2))
