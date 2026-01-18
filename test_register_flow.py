import requests
import uuid

BASE_URL = "http://127.0.0.1:8000"

def test_register():
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "SecurePassword123"
    
    print(f"Attempting to register user: {username}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/register",
            json={"username": username, "password": password}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("SUCCESS: Registration worked!")
        else:
            print("FAILED: Registration did not work.")
            
    except Exception as e:
        print(f"ERROR: Could not connect to backend: {e}")

if __name__ == "__main__":
    test_register()
