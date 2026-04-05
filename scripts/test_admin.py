import requests

BASE_URL = "http://127.0.0.1:8000/api"

def test_admin_stats():
    print("Testing admin stats endpoint...")
    # Test with non-admin (if exists) or just check 403
    resp = requests.get(f"{BASE_URL}/admin/stats?email=test@example.com")
    print(f"Non-admin response: {resp.status_code}")
    
    # Test with admin
    resp = requests.get(f"{BASE_URL}/admin/stats?email=admin@test.com")
    print(f"Admin response: {resp.status_code}")
    if resp.status_code == 200:
        print(f"Stats: {resp.json()}")

def test_login_role():
    print("\nTesting login response for admin role...")
    data = {
        "email": "admin@test.com",
        "password": "admin123"
    }
    resp = requests.post(f"{BASE_URL}/login", json=data)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        print(f"User info: {resp.json()['user']}")

if __name__ == "__main__":
    try:
        test_login_role()
        test_admin_stats()
    except Exception as e:
        print(f"Error: {e}")
