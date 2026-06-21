import os
import sys
import pandas as pd

def load_and_validate_dataset():
    # 1. Locate the real Hinglish dataset
    real_dataset_path = "data/datasets/hinglish_sentiment_v1.csv"  # Update with your precise source file name
    target_sample_path = "data/datasets/sample.csv"
    
    if not os.path.exists(real_dataset_path):
        raise FileNotFoundError(f"Real Hinglish dataset not found at {real_dataset_path}")
        
    df = pd.read_csv(real_dataset_path)
    
    # 2. Validate parameters
    n_samples = len(df)
    missing_values = df.isnull().sum().sum()
    duplicate_rows = df.duplicated().sum()
    class_dist = df['sentiment'].value_counts(normalize=True).to_dict()
    
    print("=== DATASET VALIDATION REPORT ===")
    print(f"Row Count: {n_samples}")
    print(f"Missing Values: {missing_values}")
    print(f"Duplicates: {duplicate_rows}")
    print(f"Class Distribution: {class_dist}")
    
    # Strict Guardrail Enforcement
    if n_samples < 1000:
        print("CRITICAL: Dataset size < 1000 samples. Aborting evaluation pipeline.")
        sys.exit(1)
        
    if n_samples <= 2000:
        raise ValueError(f"Aborting: Dataset must have strictly more than 2000 samples. Found: {n_samples}")
        
    # Overwrite the placeholder sample.csv with the verified full dataset
    df.to_csv(target_sample_path, index=False)
    print(f"Successfully replaced {target_sample_path} with validated production data.")
    
    return df