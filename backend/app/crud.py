from sqlalchemy.orm import Session
from .models.experiment import Experiment
from .schemas.experiment import ExperimentCreate


def create_experiment(db: Session, experiment: ExperimentCreate):
    db_obj = Experiment(
        name=experiment.name,
        dataset_path=experiment.dataset_path,
        status='pending',
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_experiment(db: Session, experiment_id: int):
    return db.query(Experiment).filter(Experiment.id == experiment_id).first()


def list_experiments(db: Session, skip: int = 0, limit: int = 50):
    return db.query(Experiment).offset(skip).limit(limit).all()


def update_experiment_status(db: Session, experiment_id: int, status: str, metrics: str | None = None):
    obj = get_experiment(db, experiment_id)
    if obj:
        obj.status = status
        if metrics is not None:
            obj.metrics = metrics
        db.commit()
        db.refresh(obj)
    return obj
