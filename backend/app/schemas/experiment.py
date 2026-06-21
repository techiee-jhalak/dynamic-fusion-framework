from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ExperimentCreate(BaseModel):
    name: str
    dataset_path: str
    output_dir: str = 'research_pipeline/outputs'

class ExperimentRead(BaseModel):
    id: int
    name: str
    dataset_path: str
    status: str
    metrics: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
