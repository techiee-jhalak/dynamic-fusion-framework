from pathlib import Path
import pandas as pd
from research_pipeline.run_pipeline import run

if __name__ == '__main__':
    input_path = Path('data/sail_cleaned.csv')
    output_dir = Path('research_pipeline/outputs')
    output_dir.mkdir(parents=True, exist_ok=True)
    run(str(input_path), str(output_dir), text_col='text', label_col='sentiment')
