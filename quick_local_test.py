import json
from src import score

def main():
    try:
        score.init()
    except Exception as e:
        print("init() failed:", e)
        return

    payload = {
        "features": {
            "amount": 100,
            "hour_of_day": 14,
            "avg_monthly_spend": 500,
            "customer_tenure_days": 365,
            "num_prev_tx_24h": 5
        }
    }

    out = score.run(json.dumps(payload))
    print("run() output:", out)

if __name__ == '__main__':
    main()
