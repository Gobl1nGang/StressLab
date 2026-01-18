from security.validator import process_credentials

# Test with valid credentials
creds = {"username": "testuser", "password": "password123"}
result = process_credentials(creds)
print(f"Result for {creds}: {result}")

# Test with invalid username
creds = {"username": "ab", "password": "password123"}
result = process_credentials(creds)
print(f"Result for {creds}: {result}")
