import requests

BASE_URL = "http://127.0.0.1:8000"

print("Testing registration with security validation...")
# Test with valid credentials
resp1 = requests.post(
    f"{BASE_URL}/register",
    json={"username": "validuser123", "password": "SecurePass123"}
)
print(f"Valid registration: {resp1.status_code} - {resp1.text[:100]}")

# Test with invalid username (too short)
resp2 = requests.post(
    f"{BASE_URL}/register",
    json={"username": "ab", "password": "SecurePass123"}
)
print(f"Invalid username: {resp2.status_code} - {resp2.text[:100]}")

# Test with weak password (too short)
resp3 = requests.post(
    f"{BASE_URL}/register",
    json={"username": "validuser456", "password": "short"}
)
print(f"Weak password: {resp3.status_code} - {resp3.text[:100]}")

# Test with SQL injection attempt
resp4 = requests.post(
    f"{BASE_URL}/register",
    json={"username": "admin' OR '1'='1", "password": "SecurePass123"}
)
print(f"SQL injection attempt: {resp4.status_code} - {resp4.text[:100]}")
