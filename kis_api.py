import requests
import json
from config import APP_KEY, APP_SECRET, BASE_URL, ACCOUNT_NO
from auth import TokenManager

class KisApi:
    def __init__(self):
        self.token_manager = TokenManager()
        self.base_url = BASE_URL
        self.account_no = ACCOUNT_NO

    def _get_header(self, tr_id):
        token = self.token_manager.get_token()
        if not token:
            raise Exception("Failed to get access token")
            
        return {
            "content-type": "application/json",
            "authorization": f"Bearer {token}",
            "appkey": APP_KEY,
            "appsecret": APP_SECRET,
            "tr_id": tr_id
        }

    def order_stock(self, stock_code, qty, buy_sell):
        """
        Place an order.
        buy_sell: 'buy' or 'sell'
        qty: quantity (int)
        price: '0' for market price (since we are doing market price orders)
        """
        path = "/uapi/domestic-stock/v1/trading/order-cash"
        url = f"{self.base_url}{path}"
        
        # VTTC0802U : Buy (Virtual) / TTTC0802U : Buy (Real)
        # VTTC0801U : Sell (Virtual) / TTTC0801U : Sell (Real)
        # Assuming Virtual Trading for now based on BASE_URL in config.py
        # If BASE_URL contains 'openapivts', it's virtual.
        
        is_virtual = "openapivts" in self.base_url
        
        if buy_sell == 'buy':
            tr_id = "VTTC0802U" if is_virtual else "TTTC0802U"
        else:
            tr_id = "VTTC0801U" if is_virtual else "TTTC0801U"
            
        headers = self._get_header(tr_id)
        
        # Split account no (e.g. "12345678-01" -> "12345678", "01")
        acc_parts = self.account_no.split('-')
        if len(acc_parts) != 2:
            raise ValueError(f"Invalid Account No format: {self.account_no}")
            
        body = {
            "CANO": acc_parts[0],
            "ACNT_PRDT_CD": acc_parts[1],
            "PDNO": stock_code,
            "ORD_DVSN": "01", # 01: Market Price (시장가)
            "ORD_QTY": str(qty),
            "ORD_UNPR": "0", # 0 for market price
        }
        
        print(f"Sending {buy_sell} order for {stock_code} (Qty: {qty})...")
        
        try:
            res = requests.post(url, headers=headers, data=json.dumps(body))
            res.raise_for_status()
            data = res.json()
            
            if data['rt_cd'] == '0':
                print(f"Order Successful: {data['msg1']}")
                return True, data
            else:
                print(f"Order Failed: {data['msg1']} (Code: {data['msg_cd']})")
                return False, data
                
        except Exception as e:
            print(f"Error placing order: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return False, str(e)

    def buy(self, stock_code, qty=1):
        return self.order_stock(stock_code, qty, 'buy')

    def sell(self, stock_code, qty=1):
        return self.order_stock(stock_code, qty, 'sell')

    def get_stock_info(self, stock_code):
        """
        종목의 현재가 및 거래금액 정보 조회
        """
        path = "/uapi/domestic-stock/v1/quotations/inquire-price"
        url = f"{self.base_url}{path}"
        
        is_virtual = "openapivts" in self.base_url
        tr_id = "VTTC0802R" if is_virtual else "FHKST01010100"
        
        headers = self._get_header(tr_id)
        
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }
        
        try:
            res = requests.get(url, headers=headers, params=params)
            res.raise_for_status()
            data = res.json()
            
            if data['rt_cd'] == '0':
                output = data.get('output', {})
                return {
                    'stock_code': stock_code,
                    'stock_name': output.get('prdt_name', ''), # 종목명
                    'stck_prpr': int(output.get('stck_prpr', 0)), # 현재가 (clpr)
                    'prdy_vrss': int(output.get('prdy_vrss', 0)), # 전일대비 (vs)
                    'prdy_ctrt': float(output.get('prdy_ctrt', 0.0)), # 등락률 (fltRt)
                    'stck_oprc': int(output.get('stck_oprc', 0)), # 시가 (mkp)
                    'stck_hgpr': int(output.get('stck_hgpr', 0)), # 고가 (hipr)
                    'stck_lwpr': int(output.get('stck_lwpr', 0)), # 저가 (lopr)
                    'acml_vol': int(output.get('acml_vol', 0)), # 누적거래량 (trqu)
                    'acml_tr_pbmn': int(output.get('acml_tr_pbmn', 0)), # 누적거래대금 (trPrc)
                    'trade_amount': int(output.get('acml_tr_pbmn', 0)), # Alias for consistency
                    'lstn_stcn': int(output.get('lstn_stcn', 0)), # 상장주식수 (lstgStCnt) - check if this field exists in response usually it is lstn_stcn
                    'hts_avls': int(output.get('hts_avls', 0)), # 시가총액 (mrktTotAmt)
                    'is_stock': True # 구분용
                }
            else:
                print(f"API Error: {data.get('msg1', 'Unknown error')}")
                return None
                
        except Exception as e:
            print(f"Error getting stock info: {e}")
            return None

    def get_all_stocks(self, market='ALL'):
        """
        코스피/코스닥 전체 종목 조회
        market: 'KOSPI', 'KOSDAQ', 'ALL'
        """
        stocks = []
        
        # 코스피
        if market in ['KOSPI', 'ALL']:
            kospi_stocks = self._get_market_stocks('J')
            stocks.extend(kospi_stocks)
            
        # 코스닥
        if market in ['KOSDAQ', 'ALL']:
            kosdaq_stocks = self._get_market_stocks('Q')
            stocks.extend(kosdaq_stocks)
            
        return stocks
    
    def get_daily_price(self, stock_code, start_date, end_date):
        """
        종목의 일별 시세 조회 (기간별)
        """
        path = "/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice"
        url = f"{self.base_url}{path}"
        
        is_virtual = "openapivts" in self.base_url
        tr_id = "VTTC0803R" if is_virtual else "FHKST03010100"
        
        headers = self._get_header(tr_id)
        
        # 시장 구분 코드가 필요한데, 일단 'J'(KOSPI)로 시도
        # 실제로는 종목별로 시장 구분을 정확히 넣어야 할 수 있음
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code,
            "FID_INPUT_DATE_1": start_date,  # 시작일자 (YYYYMMDD)
            "FID_INPUT_DATE_2": end_date,    # 종료일자 (YYYYMMDD)
            "FID_PERIOD_DIV_CODE": "D",      # 기간분류코드 (D:일봉, W:주봉, M:월봉, Y:년봉)
            "FID_ORG_ADJ_PRC": "0"           # 수정주가이벤트반영여부 (0:수정주가, 1:원주가)
        }
        
        try:
            res = requests.get(url, headers=headers, params=params)
            res.raise_for_status()
            data = res.json()
            
            if data['rt_cd'] == '0':
                return data.get('output2', []) # output2에 일별 데이터가 있음
            else:
                print(f"API Error ({stock_code}): {data.get('msg1', 'Unknown error')}")
                return []
                
        except Exception as e:
            print(f"Error getting daily price for {stock_code}: {e}")
            return []

    def _get_market_stocks(self, market_code):
        """
        특정 시장의 종목 리스트 조회
        market_code: 'J'(코스피), 'Q'(코스닥)
        """
        # ... (기존 코드 유지)
        print(f"  {'코스피' if market_code == 'J' else '코스닥'} 종목 조회 중...")
        return []
