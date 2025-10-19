import os
from typing import Mapping, Optional

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


def build_features(in_csv: str, out_csv: str) -> None:
    """Batch feature builder from CSV -> parquet (training pipeline).

    This function is intentionally minimal: it derives a few simple
    features and writes a parquet file. It exists for CLI/compatibility
    with other repo scripts.
    """
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    df = pd.read_csv(in_csv, parse_dates=["transaction_ts"]) if os.path.exists(in_csv) else pd.DataFrame()

    if df.empty:
        # write empty dataframe with no rows but safe schema
        pd.DataFrame().to_parquet(out_csv, index=False)
        print("Saved empty features to", out_csv)
        return

    # Basic derived features
    df = df.copy()
    df["amount"] = df["amount"].fillna(0).astype(float)
    df["amount_log"] = np.log(df["amount"] + 1)
    # hour_of_day may already exist; try to extract from transaction_ts
    if "transaction_ts" in df.columns:
        df["hour_of_day"] = pd.to_datetime(df["transaction_ts"]).dt.hour
        df["day_of_week"] = pd.to_datetime(df["transaction_ts"]).dt.dayofweek
    else:
        df["hour_of_day"] = 0
        df["day_of_week"] = 0

    # Customer-level rolling mean of previous amounts (simple proxy)
    if "customer_id" in df.columns and "transaction_ts" in df.columns:
        df = df.sort_values(["customer_id", "transaction_ts"])
        df["cust_prev_amount_mean"] = (
            df.groupby("customer_id")["amount"]
            .transform(lambda s: s.shift(1).rolling(5, min_periods=1).mean())
            .fillna(0)
        )
    else:
        df["cust_prev_amount_mean"] = 0

    # Select a reasonable set of columns to persist
    selected = [
        "amount",
        "amount_log",
        "hour_of_day",
        "day_of_week",
        "cust_prev_amount_mean",
    ]
    selected = [c for c in selected if c in df.columns]
    df[selected].to_parquet(out_csv, index=False)
    print("Saved features to", out_csv)


def transform_features_single(
    feat_dict: Mapping,
    scaler: Optional[StandardScaler] = None,
    numeric_cols=None,
    dummy_cols=None,
) -> pd.DataFrame:
    """Create a single-row DataFrame from a feature dict.

    Returns a DataFrame with one row and applies an optional scaler to
    numeric columns. Missing numeric values are filled with 0.
    """
    if numeric_cols is None:
        numeric_cols = [
            "amount",
            "amount_log",
            "cust_prev_amount_mean",
            "avg_monthly_spend",
            "customer_tenure_days",
            "num_prev_tx_24h",
        ]
    if dummy_cols is None:
        dummy_cols = ["country_US", "country_CA", "country_GB", "country_IN"]

    out = {}
    # copy provided
    for k, v in dict(feat_dict).items():
        out[k] = v

    # derived
    amt = float(out.get("amount", 0) or 0)
    out["amount_log"] = np.log(amt + 1)

    hod = out.get("hour_of_day")
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

    # ensure numeric columns present
    for c in numeric_cols:
        out.setdefault(c, 0)

    # dummy columns
    country_val = out.get("ip_geo_country") or out.get("country")
    for dc in dummy_cols:
        out.setdefault(dc, 0)
    if country_val is not None:
        key = f"country_{str(country_val).upper()}"
        if key in out:
            out[key] = 1

    df = pd.DataFrame([out])

    if scaler is not None:
        try:
            cols_to_scale = [c for c in numeric_cols if c in df.columns]
            if cols_to_scale:
                df[cols_to_scale] = scaler.transform(df[cols_to_scale])
        except Exception:
            # ignore scaler problems here
            pass

    return df


class FeatureBuilder:
    """Compatibility wrapper used by unit tests.

    Tests import this class and sometimes patch `get_customer_history`.
    """

    def __init__(self, scaler: Optional[StandardScaler] = None):
        self.scaler = scaler

    def get_customer_history(self, customer_id):
        """Return historical transactions for a customer.

        This is a placeholder; tests will patch this method when needed.
        """
        return pd.DataFrame()

    def build_features(self, row) -> dict:
        """Build a feature dict from a pandas Series or mapping.

        Returns a plain dict with numeric values for the features used by
        the unit tests.
        """
        if isinstance(row, pd.Series):
            data = row.to_dict()
        else:
            data = dict(row)

        ts = data.get("timestamp") or data.get("transaction_ts")
        if ts is not None:
            try:
                dt = pd.to_datetime(ts)
                hour = int(dt.hour)
                dow = int(dt.dayofweek)
            except Exception:
                hour = 0
                dow = 0
        else:
            hour = 0
            dow = 0

        amount = float(data.get("amount", 0) or 0)

        cust_id = data.get("customer_id")
        avg_monthly_spend = 0.0
        customer_tenure_days = 0
        num_prev_tx_24h = 0

        if cust_id is not None:
            hist = self.get_customer_history(cust_id)
            try:
                if hist is not None and not hist.empty:
                    # expect hist to be a DataFrame with 'amount' and timestamp
                    if "amount" in hist.columns:
                        avg_monthly_spend = float(hist["amount"].mean())
                    dates = pd.to_datetime(hist.get("timestamp", hist.get("transaction_ts")))
                    if not dates.empty:
                        customer_tenure_days = int((dates.max() - dates.min()).days)
                    num_prev_tx_24h = int(len(hist))
            except Exception:
                # keep defaults on any failure
                pass

        return {
            "amount": amount,
            "hour_of_day": hour,
            "day_of_week": dow,
            "avg_monthly_spend": avg_monthly_spend,
            "customer_tenure_days": customer_tenure_days,
            "num_prev_tx_24h": num_prev_tx_24h,
        }


if __name__ == "__main__":
    # Simple CLI for convenience (not used by tests)
    import sys

    if len(sys.argv) == 3:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    else:
        input_file = "data/raw/txs.csv"
        output_file = "data/features/feat_v1.parquet"

    build_features(input_file, output_file)
