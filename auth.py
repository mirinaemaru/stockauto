import json
import time
import os
import re
import requests
import importlib
import project_secrets as secrets
from config import APP_KEY, APP_SECRET, BASE_URL

SECRETS_FILE = "project_secrets.py"

class TokenManager:
    def __init__(self):
        self.secrets_file = SECRETS_FILE

    def _issue_new_token(self):
        """Issue a new access token from the API."""
        headers = {"content-type": "application/json"}
        body = {
            "grant_type": "client_credentials",
            "appkey": APP_KEY,
            "appsecret": APP_SECRET
        }
        url = f"{BASE_URL}/oauth2/tokenP"
        
        print(f"Requesting new token from: {url}")
        
        try:
            res = requests.post(url, headers=headers, data=json.dumps(body))
            res.raise_for_status()
            data = res.json()
            
            # Calculate expiration time (current time + expires_in - buffer)
            expires_in = int(data.get("expires_in", 86400))
            expiration_time = time.time() + expires_in - 60
            
            access_token = data["access_token"]
            
            self._update_secrets_file(access_token, expiration_time)
            print("New token issued and saved to project_secrets.py.")
            return access_token
            
        except Exception as e:
            print(f"Error issuing token: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None

    def _update_secrets_file(self, token, expiry):
        """Update project_secrets.py with new token and expiry."""
        try:
            with open(self.secrets_file, 'r') as f:
                content = f.read()
            
            # Update ACCESS_TOKEN
            if 'ACCESS_TOKEN =' in content:
                content = re.sub(r'ACCESS_TOKEN = ".*"', f'ACCESS_TOKEN = "{token}"', content)
            else:
                content += f'\nACCESS_TOKEN = "{token}"'
                
            # Update ACCESS_TOKEN_EXPIRY
            if 'ACCESS_TOKEN_EXPIRY =' in content:
                content = re.sub(r'ACCESS_TOKEN_EXPIRY = .*', f'ACCESS_TOKEN_EXPIRY = {expiry}', content)
            else:
                content += f'\nACCESS_TOKEN_EXPIRY = {expiry}'
                
            with open(self.secrets_file, 'w') as f:
                f.write(content)
                
            # Reload secrets module to reflect changes in current process if needed
            importlib.reload(secrets)
            
        except Exception as e:
            print(f"Error updating secrets.py: {e}")

    def get_token(self):
        """Get a valid access token (cached or new)."""
        # Reload secrets to get latest values
        importlib.reload(secrets)
        
        token = getattr(secrets, 'ACCESS_TOKEN', "")
        expiry = getattr(secrets, 'ACCESS_TOKEN_EXPIRY', 0)
        
        if token and expiry > time.time():
            # print("Using cached access token from secrets.py.")
            return token
            
        return self._issue_new_token()
