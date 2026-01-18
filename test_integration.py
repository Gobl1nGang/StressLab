import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_full_flow():
    print("1. Logging in...")
    # This uses the mock login
    login_resp = requests.post(f"{BASE_URL}/token", data={"username": "testuser", "password": "password"})
    if login_resp.status_code != 200:
        print(f"Login failed: {login_resp.text}")
        return
    
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"   Success! Token: {token[:10]}...")

    print("\n2. Running Backtest (MOCK)...")
    payload = {
        "ticker": "MOCK",
        "start_date": "2023-01-01",
        "end_date": "2023-04-01",
        "initial_capital": 100000,
        "indicators": [
            {"name": "SMA", "params": {"period": 20}}
        ],
        "rules": {
            "buy": "price > SMA",
            "sell": "price < SMA"
        }
    }
    
    resp = requests.post(f"{BASE_URL}/backtest", json=payload, headers=headers)
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"   Success! Final Capital: ${data['final_capital']:.2f}")
        print(f"   Trades: {len(data['trades'])}")
    else:
        print(f"   Failed: {resp.status_code}")
        print(f"   Response: {resp.text}")

if __name__ == "__main__":
    test_full_flow()
