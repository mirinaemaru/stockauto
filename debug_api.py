from kis_api import KisApi
import json

def check_api_response():
    kis = KisApi()
    # Test with Samsung Electronics (005930) for a short period
    data = kis.get_daily_price('005930', '20241201', '20241205')
    
    if data:
        print("First record keys:", data[0].keys())
        print("First record data:", json.dumps(data[0], indent=2, ensure_ascii=False))
    else:
        print("No data returned")

if __name__ == "__main__":
    check_api_response()
