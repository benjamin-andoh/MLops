from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from src.features import transform_features_single


app = FastAPI(title="FraudModel")

# Artifact paths (adjust if necessary)
MODEL_PATH = Path("models/run_local/model.joblib")
SCALER_PATH = Path("data/features/scaler.joblib")

# Load artifacts at import time (fail fast for model)
try:
    MODEL = joblib.load(MODEL_PATH)
    print("Loaded model from", MODEL_PATH)
except Exception as e:
    raise RuntimeError(f"Failed to load model from {MODEL_PATH}: {e}")

try:
    SCALER = joblib.load(SCALER_PATH)
    print("Loaded scaler from", SCALER_PATH)
except Exception as e:
    # If scaler not present or not fitted, fall back to identity behaviour
    from sklearn.preprocessing import StandardScaler
    print("Warning: failed to load scaler (using fresh StandardScaler):", e)
    SCALER = StandardScaler()


class PredictRequest(BaseModel):
    features: dict


@app.get("/")
def read_root():
    return {"message": "FraudModel API running"}


@app.post("/predict")
def predict(req: PredictRequest):
    try:
            # Use shared feature builder to construct the input DataFrame
            numeric_cols = ["amount", "amount_log", "cust_prev_amount_mean", "avg_monthly_spend", "customer_tenure_days", "num_prev_tx_24h"]
            dummy_cols = ["country_US", "country_CA", "country_GB", "country_IN"]

            df = transform_features_single(req.features, scaler=SCALER, numeric_cols=numeric_cols, dummy_cols=dummy_cols)

            # Align to model feature order if available (add missing cols in one op)
            if hasattr(MODEL, "feature_names_in_"):
                df = df.reindex(columns=list(MODEL.feature_names_in_), fill_value=0)

            probs = MODEL.predict_proba(df)[:, 1].tolist()
            return {"pred_proba": probs[0]}
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # Run with: uvicorn src.serve:app --host 127.0.0.1 --port 8000
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
