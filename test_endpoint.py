import requests
import time

# Test data
test_features = {
    "amount": 100.0,
    "hour_of_day": 14,
    "avg_monthly_spend": 500.0,
    "customer_tenure_days": 365,
    "num_prev_tx_24h": 5
}

print("Sending request with features:", test_features)

# Make prediction request with retries
max_retries = 3
retry_delay = 1
attempt = 0

while attempt < max_retries:
    attempt += 1
    print(f"\nAttempt {attempt} of {max_retries}")
    
    try:
        url = "http://127.0.0.1:8080/predict"

        print("Sending request to:", url)

        request_data = {"features": test_features}
        print("Request JSON:", request_data)

        response = requests.post(url, json=request_data, timeout=10)
        print("Status code:", response.status_code)
        print("Response headers:", response.headers)
        
        if response.status_code == 200:
            print("Success! Response:", response.json())
            break
        else:
            print("Error Response:", response.text)
            if attempt < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
    except requests.exceptions.ConnectionError as e:
        print("Connection Error:", str(e))
        if attempt < max_retries:
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
    except Exception as e:
        print("Other Error:", str(e))
        if attempt < max_retries:
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
else:
    print("\nFailed after all retries")