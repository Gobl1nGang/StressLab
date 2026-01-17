#!/usr/bin/env python3
"""
Integration test script to verify all components are connected properly.
Tests: Backend -> Engine -> Security -> Frontend API
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_root():
    """Test root endpoint"""
    print("Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    print(f"✓ Root endpoint: {response.json()}")

def test_authentication():
    """Test authentication"""
    print("\nTesting authentication...")
    response = requests.post(
        f"{BASE_URL}/token",
        data={"username": "johndoe", "password": "secret"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    print(f"✓ Authentication successful, token received")
    return token

def test_backtest(token):
    """Test backtest endpoint with authentication"""
    print("\nTesting backtest endpoint...")
    
    strategy_request = {
        "ticker": "AAPL",
        "indicators": [
            {"name": "SMA", "params": {"window": 20}},
            {"name": "RSI", "params": {"window": 14}}
        ],
        "rules": [],
        "initial_capital": 10000.0
    }
    
    response = requests.post(
        f"{BASE_URL}/backtest",
        json=strategy_request,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )
    
    assert response.status_code == 200
    result = response.json()
    print(f"✓ Backtest completed:")
    print(f"  - Final Capital: ${result['final_capital']:.2f}")
    print(f"  - Total Trades: {len(result['trades'])}")
    print(f"  - Equity Curve Points: {len(result['equity_curve'])}")
    return result

def test_analyze(token):
    """Test analysis endpoint"""
    print("\nTesting analysis endpoint...")
    
    strategy_request = {
        "ticker": "AAPL",
        "indicators": [
            {"name": "SMA", "params": {"window": 20}}
        ],
        "rules": [],
        "initial_capital": 10000.0
    }
    
    response = requests.post(
        f"{BASE_URL}/analyze",
        json=strategy_request,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )
    
    assert response.status_code == 200
    result = response.json()
    print(f"✓ Analysis completed:")
    print(f"  - Failure Probability: {result['failure_probability']:.2%}")
    print(f"  - Recommendation: {result['recommendation']}")

def test_unauthorized_access():
    """Test that endpoints are protected"""
    print("\nTesting unauthorized access...")
    
    strategy_request = {
        "ticker": "AAPL",
        "indicators": [],
        "rules": [],
        "initial_capital": 10000.0
    }
    
    response = requests.post(
        f"{BASE_URL}/backtest",
        json=strategy_request,
        headers={"Content-Type": "application/json"}
    )
    
    assert response.status_code == 401
    print(f"✓ Unauthorized access properly blocked")

if __name__ == "__main__":
    print("=" * 60)
    print("INTEGRATION TEST: Trading Strategy Falsifier")
    print("=" * 60)
    
    try:
        test_root()
        token = test_authentication()
        test_unauthorized_access()
        test_backtest(token)
        test_analyze(token)
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED - System is fully integrated!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
    except requests.exceptions.ConnectionError:
        print("\n✗ Cannot connect to backend. Make sure it's running on port 8000")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
