import requests

BASE_URL = "http://127.0.0.1:8000"

def test_login():
    # We'll use the user we just created or a known one
    # For this test, let's create a fresh one
    import uuid
    username = f"login_test_{uuid.uuid4().hex[:8]}"
    password = "SecurePassword123"
    
    print(f"1. Registering user: {username}")
    reg_resp = requests.post(
        f"{BASE_URL}/register",
        json={"username": username, "password": password}
    )
    
    if reg_resp.status_code != 200:
        print(f"Registration failed: {reg_resp.text}")
        return

    print(f"2. Attempting to login with: {username}")
    login_resp = requests.post(
        f"{BASE_URL}/token",
        data={"username": username, "password": password}
    )
    
    print(f"Status Code: {login_resp.status_code}")
    print(f"Response Body: {login_resp.text}")
    
    if login_resp.status_code == 200:
        print("SUCCESS: Login worked!")
    else:
        print("FAILED: Login did not work.")

if __name__ == "__main__":
    test_login()
