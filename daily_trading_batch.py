import time
import argparse
from datetime import datetime
from db.database import Database
from kis_api import KisApi

class DailyTradingBatch:
    def __init__(self):
        self.db = Database()
        self.kis = KisApi()
        
    def save_stock_price(self, info):
        """
        주식 시세 정보를 stock_price_info 테이블에 저장
        """
        if not info:
            return
            
        # Use provided date if available, else today
        bas_dt = info.get('basDt')
        if bas_dt:
             # Convert YYYYMMDD to YYYY-MM-DD
             bas_dt = f"{bas_dt[:4]}-{bas_dt[4:6]}-{bas_dt[6:]}"
        else:
             bas_dt = datetime.now().strftime("%Y-%m-%d")
        
        query = """
            INSERT INTO stock_price_info (
                basDt, srtnCd, isinCd, itmsNm, mrktCtg, 
                clpr, vs, fltRt, mkp, hipr, lopr, 
                trqu, trPrc, lstgStCnt, mrktTotAmt
            ) VALUES (
                %s, %s, %s, %s, %s, 
                %s, %s, %s, %s, %s, %s, 
                %s, %s, %s, %s
            ) ON DUPLICATE KEY UPDATE
                clpr = VALUES(clpr),
                vs = VALUES(vs),
                fltRt = VALUES(fltRt),
                mkp = VALUES(mkp),
                hipr = VALUES(hipr),
                lopr = VALUES(lopr),
                trqu = VALUES(trqu),
                trPrc = VALUES(trPrc),
                lstgStCnt = VALUES(lstgStCnt),
                mrktTotAmt = VALUES(mrktTotAmt)
        """
        
        params = (
            bas_dt,  
            info['stock_code'], 
            None, # isinCd
            info['stock_name'], 
            'KOSPI', # mrktCtg (Defaulting to KOSPI as we don't have it explicitly yet)
            info['stck_prpr'],
            info['prdy_vrss'],
            info['prdy_ctrt'],
            info['stck_oprc'],
            info['stck_hgpr'],
            info['stck_lwpr'],
            info['acml_vol'],
            info['acml_tr_pbmn'],
            info['lstn_stcn'],
            info['hts_avls']
        )
        
        self.db.execute(query, params)

    def run(self, start_date=None, end_date=None):
        print("=" * 60)
        print(f"자동매매 대상 종목 시세 저장 (기간: {start_date} ~ {end_date})")
        print("=" * 60)
        
        try:
             # Convert dates for DB (YYYYMMDD -> YYYY-MM-DD)
            s_dt_fmt = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:]}"
            e_dt_fmt = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:]}"
            
            print(f"기존 데이터 삭제 중... ({s_dt_fmt} ~ {e_dt_fmt})")
            del_query = "DELETE FROM stock_price_info WHERE basDt BETWEEN %s AND %s"
            self.db.execute(del_query, (s_dt_fmt, e_dt_fmt))
            print("기존 데이터 삭제 완료.\n")
            
            query = "SELECT code, name, gubun, trade_amount FROM stock WHERE use_yn = 'Y' ORDER BY trade_amount DESC"
            targets = self.db.fetch_all(query)
            
            print(f"총 {len(targets)}개 종목 처리 시작...\n")
            
            for i, stock in enumerate(targets, 1):
                stock_code = stock['code']
                stock_name = stock['name']
                
                print(f"{i}. [{stock_code}] {stock_name} 처리 중...")
                
                # 1. Get basic info for Shares Outstanding (lstn_stcn)
                # Since daily price API doesn't provide it.
                basic_info = self.kis.get_stock_info(stock_code)
                shares_count = 0
                if basic_info and 'lstn_stcn' in basic_info:
                     shares_count = basic_info['lstn_stcn']

                # 2. Get Daily Prices
                daily_data = self.kis.get_daily_price(stock_code, start_date, end_date)
                
                if not daily_data:
                    print(f"   -> 데이터 없음")
                    continue
                    
                print(f"   -> {len(daily_data)}일치 데이터 수신")

                for day_data in daily_data:
                    # Map fields
                    # Daily API keys: stck_bsop_date, stck_clpr, stck_oprc, stck_hgpr, stck_lwpr, acml_vol, acml_tr_pbmn, prdy_vrss, prtt_rate
                    
                    try:
                        clpr = int(day_data['stck_clpr'])
                        vs = int(day_data['prdy_vrss'])
                        
                        if shares_count > 0:
                            mrkt_tot_amt = clpr * shares_count
                        else:
                             mrkt_tot_amt = 0 
                        
                        # Calculate Fluctuation Rate (prdy_ctrt) manually if needed
                        # prtt_rate might be 0.00 or unreliable
                        prev_close = clpr - vs
                        if prev_close != 0:
                            flt_rt = (vs / prev_close) * 100
                        else:
                            flt_rt = 0.0
                             
                        info = {
                            'stock_code': stock_code,
                            'stock_name': stock_name,
                            'stck_prpr': clpr,
                            'prdy_vrss': vs,
                            'prdy_ctrt': flt_rt,
                            'stck_oprc': int(day_data['stck_oprc']),
                            'stck_hgpr': int(day_data['stck_hgpr']),
                            'stck_lwpr': int(day_data['stck_lwpr']),
                            'acml_vol': int(day_data['acml_vol']),
                            'acml_tr_pbmn': int(day_data['acml_tr_pbmn']),
                            'lstn_stcn': shares_count,
                            'hts_avls': mrkt_tot_amt,
                            'basDt': day_data['stck_bsop_date'] 
                        }
                        
                        # Use tailored save method or modify save_stock_price to accept date found in info
                        self.save_stock_price(info)
                        
                    except Exception as e:
                        print(f"   -> 데이터 변환 오류: {e}")

                time.sleep(0.1) 
                
        except Exception as e:
            print(f"오류 발생: {e}")
        finally:
            self.db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Daily Trading Batch')
    parser.add_argument('--start', type=str, help='Start Date (YYYYMMDD)')
    parser.add_argument('--end', type=str, help='End Date (YYYYMMDD)')
    
    args = parser.parse_args()
    
    # Default to today if not provided
    today = datetime.now().strftime("%Y%m%d")
    
    s_date = args.start if args.start else today
    e_date = args.end if args.end else s_date # If end not provided, same as start
    
    batch = DailyTradingBatch()
    batch.run(s_date, e_date)
