import hashlib
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path


def file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def dataset_hash_for_paths(paths):
    h = hashlib.sha256()
    for p in sorted(paths):
        if os.path.isdir(p):
            for root, _, files in os.walk(p):
                for fn in sorted(files):
                    fp = os.path.join(root, fn)
                    h.update(file_sha256(fp).encode())
        else:
            h.update(file_sha256(p).encode())
    return h.hexdigest()


def git_commit_hash():
    try:
        out = subprocess.check_output(['git', 'rev-parse', 'HEAD'])
        return out.decode().strip()
    except Exception:
        return None


def reproducibility_record(out_dir: str, dataset_paths, seed: int, hyperparams: dict):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    rec = {
        'dataset_hash': dataset_hash_for_paths(dataset_paths),
        'seed': int(seed),
        'git_commit': git_commit_hash(),
        'hyperparameters': hyperparams,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    with open(os.path.join(out_dir, 'reproducibility.json'), 'w') as f:
        json.dump(rec, f, indent=2)
    return rec
