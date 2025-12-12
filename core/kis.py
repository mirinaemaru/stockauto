import requests
import json
import time
from config import APP_KEY, APP_SECRET, BASE_URL, ACCOUNT_NO

class KISClient:
    def __init__(self):
        self.app_key = APP_KEY
        self.app_secret = APP_SECRET
        self.base_url = BASE_URL
        self.account_no = ACCOUNT_NO
        self.access_token = None
        self.is_demo = False # 데모 모드 플래그
        
    def get_access_token(self):
        """발급된 토큰이 없거나 만료 시 재발급"""
        if self.is_demo:
            self.access_token = "DEMO_TOKEN"
            return True
            
        path = "oauth2/tokenP"
        url = f"{self.base_url}/{path}"
        headers = {"content-type": "application/json"}
        body = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecret": self.app_secret
        }
        
        try:
            res = requests.post(url, headers=headers, data=json.dumps(body))
            if res.status_code == 200:
                data = res.json()
                self.access_token = data['access_token']
                print(f"Token issued: {self.access_token[:10]}...")
                return True
            else:
                print(f"Token Error: {res.text}")
                return False
        except Exception as e:
            print(f"Connection Error: {e}")
            return False

    def get_hash_key(self, datas):
        """POST 요청 시 보안을 위한 Hash Key 생성"""
        if self.is_demo:
            return "DEMO_HASH"
            
        path = "uapi/hashkey"
        url = f"{self.base_url}/{path}"
        headers = {
           "content-type": "application/json",
           "appKey": self.app_key,
           "appSecret": self.app_secret
        }
        res = requests.post(url, headers=headers, data=json.dumps(datas))
        if res.status_code == 200:
            return res.json()["HASH"]
        else:
            print(f"Hash Key Error: {res.text}")
            return None

    def get_current_price(self, code):
        """주식 현재가 조회"""
        if self.is_demo:
            # 데모용 랜덤 가격 반환
            import random
            price = random.randint(10000, 200000)
            return {'stck_prpr': str(price)}

        if not self.access_token:
            print("No access token.")
            return None
            
        path = "uapi/domestic-stock/v1/quotations/inquire-price"
        url = f"{self.base_url}/{path}"
        headers = {
            "content-type": "application/json",
            "authorization": f"Bearer {self.access_token}",
            "appKey": self.app_key,
            "appSecret": self.app_secret,
            "tr_id": "FHKST01010100" # 주식 현재가 시세
        }
        params = {
            "fid_cond_mrkt_div_code": "J",
            "fid_input_iscd": code
        }
        
        res = requests.get(url, headers=headers, params=params)
        if res.status_code == 200:
            return res.json()['output']
        else:
            print(f"Price Error: {res.text}")
            return None

    def get_balance(self):
        """계좌 잔고 및 보유 종목 조회"""
        if self.is_demo:
            # 데모용 더미 데이터 반환
            return {
                'rt_cd': '0',
                'output1': [
                    {'prdt_name': '삼성전자', 'hldg_qty': '10', 'pchs_avg_pric': '70000', 'prpr': '72500', 'evlu_pfls_rt': '3.57'},
                    {'prdt_name': 'SK하이닉스', 'hldg_qty': '5', 'pchs_avg_pric': '120000', 'prpr': '118000', 'evlu_pfls_rt': '-1.67'},
                    {'prdt_name': 'NAVER', 'hldg_qty': '3', 'pchs_avg_pric': '200000', 'prpr': '205000', 'evlu_pfls_rt': '2.50'}
                ],
                'output2': [{
                    'tot_evlu_amt': '1930000', 
                    'dnca_tot_amt': '5000000', 
                    'evlu_pfls_smtl_amt': '30000'
                }]
            }

        if not self.access_token:
            print("No access token.")
            return None

        path = "uapi/domestic-stock/v1/trading/inquire-balance"
        url = f"{self.base_url}/{path}"
        
        headers = {
            "content-type": "application/json",
            "authorization": f"Bearer {self.access_token}",
            "appKey": self.app_key,
            "appSecret": self.app_secret,
            "tr_id": "VTTC8434R" if "vts" in self.base_url else "TTTC8434R" # 모의투자/실전투자 구분
        }
        
        # 계좌번호 앞 8자리, 뒤 2자리 분리
        cano = self.account_no.split('-')[0]
        acnt_prdt_cd = self.account_no.split('-')[1]

        params = {
            "CANO": cano,
            "ACNT_PRDT_CD": acnt_prdt_cd,
            "AFHR_FLPR_YN": "N",
            "OFL_YN": "",
            "INQR_DVSN": "02",
            "UNPR_DVSN": "01",
            "FUND_STTL_ICLD_YN": "N",
            "FNCG_AMT_AUTO_RDPT_YN": "N",
            "PRCS_DVSN": "01",
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": ""
        }

        res = requests.get(url, headers=headers, params=params)
        if res.status_code == 200:
            return res.json()
        else:
            print(f"Balance Error: {res.text}")
            return None
