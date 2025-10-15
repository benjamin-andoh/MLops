# File: src/train.py
# Minimal reproducible training script. Integrate into Azure ML later.
import argparse
import os
import joblib
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, classification_report

def load_features(path):
    if path.endswith(".parquet"):
        return pd.read_parquet(path)
    else:
        return pd.read_csv(path, parse_dates=["transaction_ts"])

def train(args):
    df = load_features(args.features)
    y = df["is_fraud"].astype(int)
    # drop identifiers
    X = df.drop(columns=["is_fraud","transaction_id","transaction_ts","customer_id","merchant_id"])
    X = X.fillna(0)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=args.seed, stratify=y)
    model = RandomForestClassifier(n_estimators=args.n_estimators, random_state=args.seed, n_jobs=2)
    model.fit(X_train, y_train)
    preds = model.predict_proba(X_test)[:,1]
    auc = roc_auc_score(y_test, preds)
    print("AUC:", auc)
    # save model + metadata
    os.makedirs(args.output_dir, exist_ok=True)
    joblib.dump(model, os.path.join(args.output_dir, "model.joblib"))
    meta = {"auc": float(auc), "n_estimators": args.n_estimators, "seed": args.seed}
    with open(os.path.join(args.output_dir, "metrics.json"), "w") as f:
        json.dump(meta, f)
    print("Saved model and metrics to", args.output_dir)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--features", type=str, required=True)
    p.add_argument("--output_dir", type=str, default="models/run_1")
    p.add_argument("--n_estimators", type=int, default=100)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()
    train(args)
