# Initial placeholder analysis file. Used to setup github workflows and CI/CD pipelines.
from pathlib import Path
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = REPO_ROOT / "data"
OUT_DIR = REPO_ROOT / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

files = sorted([p.name for p in DATA_DIR.rglob("*") if p.is_file()])

df = pd.DataFrame({
    "n_files_in_data": [len(files)],
    "example_files": [", ".join(files[:10])]
})

df.to_csv(OUT_DIR / "summary.csv", index=False)
print("Wrote outputs/summary.csv")