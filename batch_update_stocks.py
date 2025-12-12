import time
import requests
from db.database import Database
from kis_api import KisApi

class StockBatchUpdater:
    def __init__(self):
        self.db = Database()
        self.kis = KisApi()
        self.min_trade_amount = 100000000  # 1억
        
    def reset_all_stocks(self):
        """모든 종목의 use_yn을 'N'으로 초기화"""
        print("모든 종목의 use_yn을 'N'으로 초기화 중...")
        query = "UPDATE stock SET use_yn = 'N'"
        self.db.execute(query)
        print("초기화 완료")
        
    def get_all_stock_codes_from_krx(self):
        """
        한국거래소(KRX)에서 전체 종목 코드 조회
        OTP 방식을 사용하여 KOSPI + KOSDAQ 전체 종목 조회
        """
        print("KRX에서 전체 종목 리스트 다운로드 중...")
        
        try:
            # Step 1: OTP 발급
            gen_otp_url = 'http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd'
            gen_otp_data = {
                'mktId': 'ALL',  # ALL: 전체, STK: 코스피, KSQ: 코스닥
                'trdDd': time.strftime('%Y%m%d'),  # 오늘 날짜
                'money': '1',
                'csvxls_isNo': 'false',
                'name': 'fileDown',
                'url': 'dbms/MDC/STAT/standard/MDCSTAT01901'
            }
            
            headers = {'User-Agent': 'Mozilla/5.0'}
            otp_response = requests.post(gen_otp_url, data=gen_otp_data, headers=headers)
            otp = otp_response.text
            
            print(f"  OTP 발급: {otp[:20]}...")
            
            # Step 2: OTP로 데이터 다운로드
            down_url = 'http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd'
            down_data = {'code': otp}
            
            response = requests.post(down_url, data=down_data, headers=headers)
            response.encoding = 'euc-kr'
            
            print(f"  응답 길이: {len(response.text)} bytes")
            
            # CSV 파싱
            lines = response.text.strip().split('\n')
            stock_codes = []
            
            print(f"  총 {len(lines)}줄 데이터")
            
            for i, line in enumerate(lines):
                if i == 0:  # 헤더
                    print(f"  헤더: {line[:100]}")
                    continue
                    
                if line.strip():
                    parts = line.split(',')
                    if len(parts) >= 2:
                        code = parts[0].strip().strip('"')
                        name = parts[1].strip().strip('"')
                        if code and len(code) == 6 and code.isdigit():
                            stock_codes.append({'code': code, 'name': name})
            
            print(f"총 {len(stock_codes)}개 종목 조회 완료")
            
            if len(stock_codes) == 0:
                print("KRX 조회 실패. 기존 DB 종목 사용...")
                return self.get_existing_stocks()
                
            return stock_codes
            
        except Exception as e:
            print(f"KRX 종목 조회 실패: {e}")
            import traceback
            traceback.print_exc()
            print("대신 DB의 기존 종목 사용...")
            return self.get_existing_stocks()
    
    def get_existing_stocks(self):
        """DB에 이미 등록된 종목 조회"""
        query = "SELECT code, name FROM stock"
        results = self.db.fetch_all(query)
        return [{'code': row['code'], 'name': row['name']} for row in results]
    
    def update_stock_info(self, stock_code, stock_name=''):
        """종목 정보 조회 및 DB 업데이트"""
        info = self.kis.get_stock_info(stock_code)
        
        if not info:
            return False
            
        trade_amount = info['trade_amount']
        if not stock_name:
            stock_name = info['stock_name']
        
        # stock 테이블에 UPSERT
        query = """
            INSERT INTO stock (code, name, gubun, trade_amount, use_yn)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                trade_amount = VALUES(trade_amount),
                use_yn = VALUES(use_yn)
        """
        
        # 거래금액이 1억 이상이면 use_yn='Y', 아니면 'N'
        use_yn = 'Y' if trade_amount >= self.min_trade_amount else 'N'
        
        self.db.execute(query, (stock_code, stock_name, 'STOCK', trade_amount, use_yn))
        
        if use_yn == 'Y':
            status = "✓"
            print(f"  {status} {stock_code} ({stock_name}): {trade_amount:,}원 -> use_yn={use_yn}")
        
        return True
    
    def register_initial_stocks(self, stocks):
        """
        KRX에서 조회한 전체 종목을 DB에 등록 (기초 데이터)
        이미 존재하는 종목은 무시 (INSERT IGNORE)
        """
        print("전체 종목 DB 등록 중...")
        
        # 대량 데이터 처리를 위해 executemany 사용
        query = """
            INSERT IGNORE INTO stock (code, name, gubun, use_yn, trade_amount)
            VALUES (%s, %s, 'STOCK', 'N', 0)
        """
        
        data = [(s['code'], s['name']) for s in stocks]
        
        try:
            # executemany가 Database 클래스에 없으므로 반복문으로 처리하거나
            # Database 클래스에 executemany를 추가해야 함.
            # 여기서는 안전하게 반복문으로 처리하되, 성능을 위해 트랜잭션 처리 권장
            # 하지만 현재 Database 클래스 구조상 단순 반복 실행
            
            count = 0
            for item in data:
                self.db.execute(query, item)
                count += 1
                if count % 1000 == 0:
                    print(f"  {count}개 등록 완료...")
                    
            print(f"총 {count}개 종목 등록/확인 완료")
            
        except Exception as e:
            print(f"종목 등록 중 오류 발생: {e}")

    def run_batch(self):
        """배치 작업 실행"""
        print("=" * 60)
        print("거래금액 필터링 배치 작업 시작")
        print(f"기준: 거래금액 {self.min_trade_amount:,}원 이상")
        print("=" * 60)
        
        # 1. 초기화
        self.reset_all_stocks()
        
        # 2. 전체 종목 조회 (KRX)
        all_stocks = self.get_all_stock_codes_from_krx()
        print(f"\n조회 대상 종목 수: {len(all_stocks)}개\n")
        
        # [NEW] 2-1. 전체 종목 DB 등록 (기초 데이터)
        self.register_initial_stocks(all_stocks)
        
        # 3. 각 종목 정보 업데이트
        success_count = 0
        active_count = 0
        
        for i, stock in enumerate(all_stocks, 1):
            stock_code = stock['code']
            stock_name = stock['name']
            
            if i % 100 == 0:
                print(f"진행 중... [{i}/{len(all_stocks)}]")
            
            if self.update_stock_info(stock_code, stock_name):
                success_count += 1
                
            # API 호출 제한 고려 (초당 10건)
            time.sleep(0.1)
        
        # 4. 결과 요약
        print("\n" + "=" * 60)
        print("배치 작업 완료")
        print(f"처리 성공: {success_count}/{len(all_stocks)}개")
        
        # use_yn='Y'인 종목 수 조회
        result = self.db.fetch_one("SELECT COUNT(*) as cnt FROM stock WHERE use_yn = 'Y'")
        active_count = result['cnt'] if result else 0
        print(f"활성 종목(use_yn='Y'): {active_count}개")
        print("=" * 60)

if __name__ == "__main__":
    updater = StockBatchUpdater()
    updater.run_batch()
