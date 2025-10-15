# File: src/features.py
import pandas as pd
import os
import sys
import numpy as np
from sklearn.preprocessing import StandardScaler

FEATURE_ORDER = [
    "amount","hour_of_day","day_of_week","customer_tenure_days","avg_monthly_spend","num_prev_tx_24h"
]

def build_features(in_csv, out_csv):
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    df = pd.read_csv(in_csv, parse_dates=["transaction_ts"])
    # Simple deterministic features
    df["amount_log"] = (df["amount"] + 1).apply(lambda x: np.log(x))
    df["hour_sin"] = np.sin(2 * np.pi * df["hour_of_day"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour_of_day"] / 24)
    # customer historic: naive approach for demo
    df = df.sort_values(["customer_id","transaction_ts"])
    df["cust_prev_amount_mean"] = df.groupby("customer_id")["amount"].transform(lambda s: s.shift(1).rolling(5, min_periods=1).mean()).fillna(0)
    # scale numeric features
    numeric_cols = ["amount","amount_log","cust_prev_amount_mean","avg_monthly_spend","customer_tenure_days","num_prev_tx_24h"]
    # one-hot encode categorical columns
    categorical_cols = ["merchant_category", "currency", "device_fingerprint", "ip_geo_country"]
    df = pd.get_dummies(df, columns=categorical_cols, prefix=["mc", "curr", "dev", "country"], drop_first=True)
    scaler = StandardScaler()
    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
    # save scaler
    import joblib
    os.makedirs("data/features", exist_ok=True)
    joblib.dump(scaler, "data/features/scaler.joblib")
    # save features
    selected = ["transaction_id","transaction_ts","customer_id","merchant_id","is_fraud"] + [c for c in df.columns if c not in ["transaction_id","transaction_ts","customer_id","merchant_id","is_fraud"]]
    df[selected].to_parquet(out_csv, index=False)
    print("Saved features to", out_csv)


def transform_features_single(feat_dict, scaler=None, numeric_cols=None, dummy_cols=None):
    """Create a single-row DataFrame from a feature dict.

    - feat_dict: mapping of feature names to values (may be partial)
    - scaler: optional fitted scaler to apply to numeric columns
    - numeric_cols: list of numeric columns to ensure/scale (defaults used from training)
    - dummy_cols: list of one-hot/dummy column names to ensure exist

    Returns: pd.DataFrame with one row
    """
    if numeric_cols is None:
        numeric_cols = ["amount", "amount_log", "cust_prev_amount_mean", "avg_monthly_spend", "customer_tenure_days", "num_prev_tx_24h"]
    if dummy_cols is None:
        # common country dummies used in serving examples; callers can pass a fuller list
        dummy_cols = ["country_US", "country_CA", "country_GB", "country_IN"]

    # Build a plain dict first to avoid repeated DataFrame inserts
    out = {}

    # copy over provided features
    for k, v in feat_dict.items():
        out[k] = v

    # Derived features
    amt = float(feat_dict.get("amount", 0))
    out["amount_log"] = np.log(amt + 1)

    hod = feat_dict.get("hour_of_day")
    if hod is not None:
        try:
            hodf = float(hod)
            out["hour_sin"] = np.sin(2 * np.pi * hodf / 24)
            out["hour_cos"] = np.cos(2 * np.pi * hodf / 24)
        except Exception:
            out["hour_sin"] = 0
            out["hour_cos"] = 0
    else:
        out["hour_sin"] = 0
        out["hour_cos"] = 0

    # ensure numeric columns exist
    for c in numeric_cols:
        if c not in out:
            out[c] = 0

    # handle dummy columns: if input contains ip_geo_country or similar, set the matching dummy
    country_val = feat_dict.get("ip_geo_country") or feat_dict.get("country")
    for dc in dummy_cols:
        out[dc] = 0
    if country_val is not None:
        key = f"country_{str(country_val).upper()}"
        if key in out:
            out[key] = 1

    # Build DataFrame
    df = pd.DataFrame([out])

    # Apply scaler to numeric columns if provided
    if scaler is not None:
        try:
            # Only apply to columns that exist in DF and scaler expects
            cols_to_scale = [c for c in numeric_cols if c in df.columns]
            if len(cols_to_scale) > 0:
                df[cols_to_scale] = scaler.transform(df[cols_to_scale])
        except Exception:
            # if scaler not fitted or mismatch, skip scaling
            pass

    return df


if __name__ == "__main__":
    # Use command line args if provided, else use defaults
    if len(sys.argv) == 3:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    else:
        # Default values
        input_file = "data/raw/txs.csv"
        output_file = "data/features/feat_v1.parquet"
        print(f"Using default paths: {input_file} -> {output_file}")
    
    build_features(input_file, output_file)