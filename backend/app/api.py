import os
import joblib
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from pathlib import Path
from sqlalchemy.orm import Session
from research_pipeline.run_pipeline import run as run_pipeline
from research_pipeline.training.engine import load_and_enrich, train_logistic_cv, evaluate_fusion
from research_pipeline.training.generate_paper_outputs import generate_paper_outputs
from research_pipeline.src.models.transformer_wrapper import TransformerWrapper
from research_pipeline.src.models.vader_model import VaderWrapper
from research_pipeline.src.models.fusion_models import dynamic_noise_aware_fusion
from backend.app.database import get_db
from backend.app.schemas.experiment import ExperimentCreate, ExperimentRead
from backend.app import crud

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / 'ml_models' / 'sail_fusion_model.joblib'

router = APIRouter()

class TrainRequest(BaseModel):
    dataset_path: str
    output_dir: str = 'research_pipeline/outputs'
    seed: int = 42
    cv: int = 5

class EvaluateRequest(BaseModel):
    dataset_path: str
    output_dir: str = 'research_pipeline/outputs'

class PredictRequest(BaseModel):
    dataset_path: str
    output_path: str = 'research_pipeline/outputs/predictions.csv'
    w1: float = 0.1
    w2: float = 1.0

class NoiseAnalysisRequest(BaseModel):
    dataset_path: str
    output_dir: str = 'research_pipeline/outputs'

class GeneratePaperRequest(BaseModel):
    dataset_path: str
    output_dir: str = 'paper_outputs'

class ExportRequest(BaseModel):
    dataset_path: str
    output_dir: str = 'paper_outputs'

@router.post('/train')
async def train_endpoint(request: TrainRequest, db: Session = Depends(get_db)):
    if not Path(request.dataset_path).exists():
        raise HTTPException(status_code=404, detail='Dataset path not found')
    experiment = crud.create_experiment(db, ExperimentCreate(name='training-job', dataset_path=request.dataset_path))
    enriched = load_and_enrich(request.dataset_path)
    result = train_logistic_cv(enriched, text_col='text', label_col='label', out_dir=request.output_dir, seed=request.seed, cv=request.cv)
    crud.update_experiment_status(db, experiment.id, 'completed', metrics=str(result.to_dict(orient='records') if hasattr(result, 'to_dict') else str(result)))
    return {'status': 'ok', 'result': result}

@router.post('/evaluate')
async def evaluate_endpoint(request: EvaluateRequest):
    if not Path(request.dataset_path).exists():
        raise HTTPException(status_code=404, detail='Dataset path not found')
    enriched = load_and_enrich(request.dataset_path)
    result = evaluate_fusion(enriched, request.output_dir)
    return {'status': 'ok', 'result': result}

@router.post('/predict')
async def predict_endpoint(request: PredictRequest):
    if not Path(request.dataset_path).exists():
        raise HTTPException(status_code=404, detail='Dataset path not found')
    if not MODEL_PATH.exists():
        raise HTTPException(status_code=500, detail='Model artifact not found')

    artifact = joblib.load(MODEL_PATH)
    model = artifact['pipeline']
    df = pd.read_csv(request.dataset_path)
    texts = df['text'].astype(str).tolist()
    preds = model.predict(texts)
    probs = model.predict_proba(texts)
    results = []
    for pred, prob in zip(preds, probs):
        label = int(pred)
        results.append({
            'sentiment': 'positive' if label == 2 else 'negative' if label == 0 else 'neutral',
            'confidence': float(max(prob)),
            'probabilities': [float(v) for v in prob],
        })

    out_df = df.copy()
    out_df['pred'] = preds
    out_df['confidence'] = [r['confidence'] for r in results]
    out_dir = Path(request.output_path).parent
    out_dir.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(request.output_path, index=False)
    return {'status': 'ok', 'output_path': request.output_path, 'predictions': len(out_df), 'results_sample': results[:20]}

@router.post('/noise-analysis')
async def noise_analysis_endpoint(request: NoiseAnalysisRequest):
    if not Path(request.dataset_path).exists():
        raise HTTPException(status_code=404, detail='Dataset path not found')
    enriched = Path(request.output_dir) / 'enriched_dataset.csv'
    from research_pipeline.run_pipeline import run
    run(request.dataset_path, request.output_dir)
    return {'status': 'ok', 'enriched_path': str(enriched)}

@router.post('/generate-paper-results')
async def generate_paper_results_endpoint(request: GeneratePaperRequest):
    if not Path(request.dataset_path).exists():
        raise HTTPException(status_code=404, detail='Dataset path not found')
    result = generate_paper_outputs(request.dataset_path, request.output_dir)
    return {'status': 'ok', 'output_dir': request.output_dir, 'summary': {k: v.shape[0] if hasattr(v, 'shape') else None for k, v in result.items()}}

@router.post('/export')
async def export_endpoint(request: ExportRequest):
    if not Path(request.dataset_path).exists():
        raise HTTPException(status_code=404, detail='Dataset path not found')
    from research_pipeline.src.utils.io import save_all_formats
    import pandas as pd
    df = pd.read_csv(request.dataset_path)
    out = save_all_formats(df, request.output_dir, 'exported_dataset')
    return {'status': 'ok', 'exports': out}

@router.post('/experiments')
def create_experiment(request: ExperimentCreate, db: Session = Depends(get_db)):
    return crud.create_experiment(db, request)

@router.get('/experiments/{experiment_id}', response_model=ExperimentRead)
def get_experiment(experiment_id: int, db: Session = Depends(get_db)):
    experiment = crud.get_experiment(db, experiment_id)
    if not experiment:
        raise HTTPException(status_code=404, detail='Experiment not found')
    return experiment

@router.get('/experiments')
def list_experiments(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return crud.list_experiments(db, skip=skip, limit=limit)
