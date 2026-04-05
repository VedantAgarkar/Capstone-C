import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_register():
    print("Testing registration...")
    data = {
        "email": "test@example.com",
        "password": "password123",
        "fullname": "Test User"
    }
    response = requests.post(f"{BASE_URL}/register", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code

def test_login():
    print("\nTesting login...")
    data = {
        "email": "test@example.com",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/login", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code

def test_sqli_email():
    print("\nTesting SQL injection protection in email field (caught by Pydantic)...")
    data = {
        "email": "admin@example.com' OR '1'='1",
        "password": "any"
    }
    response = requests.post(f"{BASE_URL}/login", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code

def test_sqli_password():
    print("\nTesting SQL injection protection in password field (caught by Parameterized Query)...")
    data = {
        "email": "test@example.com",
        "password": "' OR '1'='1"
    }
    response = requests.post(f"{BASE_URL}/login", json=data)
    print(f"Status: {response.status_code}")
    # We expect 401 because the query should look for exactly the string "' OR '1'='1" as password
    print(f"Response: {response.json()}")
    return response.status_code

if __name__ == "__main__":
    try:
        reg_status = test_register()
        if reg_status in [200, 400]:
            test_login()
            test_sqli_email()
            test_sqli_password()
    except Exception as e:
        print(f"Error: {e}")
