import requests

BASE_URL = "http://127.0.0.1:8000"

# Test login with the existing user
print("Testing login with existing user 'test'...")
login_resp = requests.post(
    f"{BASE_URL}/token", 
    data={"username": "test", "password": "test"}
)

print(f"Status: {login_resp.status_code}")
print(f"Response: {login_resp.text}")

if login_resp.status_code == 200:
    print("✓ Login successful!")
else:
    print("✗ Login failed!")
