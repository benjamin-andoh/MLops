# File: scripts/drift_monitor.py
# Periodic job: compute simple KS-test per numeric feature vs baseline and emit JSON report.
import json
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp
import os

BASELINE_PATH = os.environ.get("BASELINE_PATH","data/features/baseline.parquet")
CURRENT_PATH = os.environ.get("CURRENT_PATH","data/features/feat_v1.parquet")
OUT_REPORT = os.environ.get("DRIFT_REPORT","data/drift/report.json")
THRESHOLD = 0.1  # ks p-value threshold to signal drift (tunable)

def detect_drift(baseline_path, current_path):
    base = pd.read_parquet(baseline_path)
    cur = pd.read_parquet(current_path)
    numeric = base.select_dtypes(include=[np.number]).columns.intersection(cur.select_dtypes(include=[np.number]).columns)
    report = {}
    for col in numeric:
        stat, p = ks_2samp(base[col].dropna(), cur[col].dropna())
        report[col] = {"stat": float(stat), "p": float(p), "drift": p < THRESHOLD}
    return report

if __name__ == "__main__":
    report = detect_drift(BASELINE_PATH, CURRENT_PATH)
    os.makedirs(os.path.dirname(OUT_REPORT), exist_ok=True)
    with open(OUT_REPORT, "w") as f:
        json.dump(report, f, indent=2)
    print("Wrote drift report to", OUT_REPORT)
