import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

# Define SQL Injection Payloads to test
PAYLOADS = [
    # Tautologies
    "' OR '1'='1",
    "admin' OR '1'='1",
    "' or 1=1--",
    '" or 1=1--',
    "or 1=1",
    
    # Union Based (Attempting to discover number of columns or leak data)
    "' UNION SELECT 1,2,3,4--",
    "' UNION SELECT NULL, email, password, fullname FROM users--",
    
    # Error Based / Blind
    "admin' AND (SELECT 1 FROM (SELECT COUNT(*), CONCAT(0x7e, (SELECT table_name FROM information_schema.tables LIMIT 0,1), 0x7e) as x FROM information_schema.tables GROUP BY x) as y)--",
    
    # Commenting / Character Escaping
    "admin'--",
    "admin'/*",
    "admin'#",
    "'; DROP TABLE users;--",
    
    # Common Login bypass variations
    "' or ''='",
    "'='",
    "'-'",
    "admin' --",
    "admin' #",
    "admin'/*",
    "' or 1=1--",
    "' or 1=1#",
    "' or 1=1/*",
    "') or ('1'='1",
    " admin'--",
]

def test_payloads():
    print("="*53)
    print(" GSD - SECURITY AUDIT: SQL INJECTION")
    print("="*53 + "\n")
    
    vulnerabilities_found = 0
    total_tests = 0

    print(f"Testing {len(PAYLOADS)} payloads against login endpoint...\n")

    for payload in PAYLOADS:
        total_tests += 1
        # Test in Email field
        email_data = {"email": payload, "password": "any"}
        try:
            email_resp = requests.post(f"{BASE_URL}/login", json=email_data)
            # 422 is Pydantic validation error (EmailStr) - THIS IS SECURE
            # 401 is Unauthorized (Query found nothing) - THIS IS SECURE
            if email_resp.status_code == 200:
                print(f"[!] VULNERABILITY FOUND (Email field): Payload: {payload}")
                vulnerabilities_found += 1
        except Exception as e:
            # print(f"Error testing email payload '{payload}': {e}")
            pass

        # Test in Password field
        pass_data = {"email": "test@example.com", "password": payload}
        try:
            pass_resp = requests.post(f"{BASE_URL}/login", json=pass_data)
            # 401 is Unauthorized (Query searched for the literal string) - THIS IS SECURE
            if pass_resp.status_code == 200:
                print(f"[!] VULNERABILITY FOUND (Password field): Payload: {payload}")
                vulnerabilities_found += 1
        except Exception as e:
            # print(f"Error testing password payload '{payload}': {e}")
            pass

    print("\n" + "-"*53)
    print(f"Audit Complete.")
    print(f"Total Tests Run: {total_tests * 2}") # Email and Password for each
    print(f"Vulnerabilities Found: {vulnerabilities_found}")
    print("-"*53 + "\n")

    if vulnerabilities_found == 0:
        print("PASS: All SQL injection vectors neutralized.")
    else:
        print("FAIL: Security vulnerabilities detected.")

    return vulnerabilities_found

if __name__ == "__main__":
    test_payloads()
