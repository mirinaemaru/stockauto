# Korea Investment & Securities API Config

# API Credentials (KEEP SAFE!)
try:
    from secrets import APP_KEY, APP_SECRET, ACCOUNT_NO
    from secrets import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
except ImportError:
    print("Warning: secrets.py not found. Please create it with your credentials.")
    APP_KEY = None
    APP_SECRET = None
    ACCOUNT_NO = None
    DB_HOST = "localhost"
    DB_PORT = 3306
    DB_USER = "root"
    DB_PASSWORD = ""
    DB_NAME = "stockauto"

# URL Settings
# Real Trading: https://openapi.koreainvestment.com:9443
# Virtual Trading: https://openapivts.koreainvestment.com:29443
BASE_URL = "https://openapi.koreainvestment.com:9443" 
