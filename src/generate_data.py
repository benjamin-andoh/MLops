# File: src/generate_data.py
# Usage: python src/generate_data.py --rows 10000 \
#     --out data/raw/transactions.csv --seed 42
import argparse
import csv
import datetime
import json
import os
import random
import uuid

SCHEMA = [
    "transaction_id",
    "transaction_ts",
    "customer_id",
    "merchant_id",
    "amount",
    "currency",
    "merchant_category",
    "device_fingerprint",
    "ip_geo_country",
    "hour_of_day",
    "day_of_week",
    "customer_tenure_days",
    "avg_monthly_spend",
    "num_prev_tx_24h",
    "is_fraud",
]


def sample_merchant_category():
    cats = [
        "retail",
        "grocery",
        "travel",
        "entertainment",
        "utilities",
        "electronics",
    ]
    weights = [0.25, 0.25, 0.1, 0.15, 0.15, 0.1]
    return random.choices(cats, weights)[0]


def generate_row(now, idx):
    # random timestamp within the last 90 days
    secs = random.randint(0, 86400 * 90)
    ts = now - datetime.timedelta(seconds=secs)
    cust_num = random.randint(1, 20000)
    cust = f"C{cust_num}"
    merch_num = random.randint(1, 5000)
    merch = f"M{merch_num}"
    amt = max(0.5, random.gammavariate(2, 75))
    merchant_category = sample_merchant_category()
    device_num = random.randint(1, 100000)
    device = f"D{device_num}"
    country = random.choice(
        [
            "CA",
            "US",
            "GB",
            "AU",
            "IN",
        ]
    )
    hour = ts.hour
    dow = ts.weekday()
    tenure = random.randint(1, 5000)
    avg_month = max(5, random.gammavariate(2, 200))
    # Use Poisson-like behavior when available; otherwise fallback to randint
    if hasattr(random, "poissonvariate"):
        prev24 = random.poissonvariate(0.5)
    else:
        prev24 = random.randint(0, 5)

    # fraud rule: low probability but correlated with large amounts
    # and certain merchant categories
    base_prob = 0.02
    if amt > 200:
        base_prob += 0.03
    if merchant_category == "electronics":
        base_prob += 0.01
    if country == "IN":
        base_prob += 0.005
    is_fraud = 1 if random.random() < base_prob else 0
    return {
        "transaction_id": str(uuid.uuid4()),
        "transaction_ts": ts.isoformat(),
        "customer_id": cust,
        "merchant_id": merch,
        "amount": round(amt, 2),
        "currency": "CAD",
        "merchant_category": merchant_category,
        "device_fingerprint": device,
        "ip_geo_country": country,
        "hour_of_day": hour,
        "day_of_week": dow,
        "customer_tenure_days": tenure,
        "avg_monthly_spend": round(avg_month, 2),
        "num_prev_tx_24h": prev24,
        "is_fraud": is_fraud,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--rows", type=int, default=10000)
    p.add_argument("--out", type=str, default="data/raw/transactions.csv")
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()
    random.seed(args.seed)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    now = datetime.datetime.utcnow()
    with open(args.out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SCHEMA)
        writer.writeheader()
        for i in range(args.rows):
            writer.writerow(generate_row(now, i))
    # write metadata about generation
    meta = {
        "rows": args.rows,
        "seed": args.seed,
        "generated_at": now.isoformat(),
    }
    meta_path = f"{os.path.splitext(args.out)[0]}_meta.json"
    with open(meta_path, "w") as mf:
        json.dump(meta, mf, indent=2)
    print("Wrote", args.out)


if __name__ == "__main__":
    main()
