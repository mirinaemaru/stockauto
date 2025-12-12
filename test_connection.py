from auth import TokenManager
from config import APP_KEY, APP_SECRET

def test_connection():
    print("=== Starting Connection Test with secrets.py Caching ===")
    
    if not APP_KEY or not APP_SECRET:
        print("Error: APP_KEY or APP_SECRET not found in config/secrets.")
        return

    manager = TokenManager()
    token = manager.get_token()
    
    if token:
        print("\nConnection Test PASSED: Successfully retrieved access token.")
        print(f"Token (first 20 chars): {token[:20]}...")
    else:
        print("\nConnection Test FAILED: Could not retrieve access token.")

if __name__ == "__main__":
    test_connection()
