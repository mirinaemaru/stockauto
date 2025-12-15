import time
from pykrx import stock
from db.database import Database

class StockBatchUpdater:
    def __init__(self):
        self.db = Database()

    def reset_all_stocks(self):
        """
        데이터 초기화: stock테이블의 사용여부(use_yn='N')를 초기화
        """
        print("모든 종목의 use_yn을 'N'으로 초기화 중...")
        query = "UPDATE stock SET use_yn = 'N'"
        self.db.execute(query)
        print("초기화 완료")

    def update_stock_master(self):
        """
        데이터 수집 및 저장:
        1. pykrx를 이용해 KOSPI, KOSDAQ 종목 리스트 수집
        2. DB에 저장 (신규: 추가, 기존: 업데이트)
        """
        markets = [("KOSPI", "KOSPI"), ("KOSDAQ", "KOSDAQ")]
        
        total_upsert_count = 0
        
        for market_ticker, market_gubun in markets:
            print(f"[{market_gubun}] 종목 리스트 수집 중...")
            try:
                # pykrx를 통해 해당 마켓의 티커 리스트 가져오기
                tickers = stock.get_market_ticker_list(market=market_ticker)
                
                print(f"  > {len(tickers)}개 종목 발견. DB 업데이트 시작...")
                
                for code in tickers:
                    name = stock.get_market_ticker_name(code)
                    
                    # 데이터 저장: 코드, 이름, 구분, 사용여부='Y'
                    query = """
                        INSERT INTO stock (code, name, gubun, use_yn)
                        VALUES (%s, %s, %s, 'Y')
                        ON DUPLICATE KEY UPDATE
                            name = VALUES(name),
                            gubun = VALUES(gubun),
                            use_yn = 'Y'
                    """
                    
                    self.db.execute(query, (code, name, market_gubun))
                    total_upsert_count += 1
                    
                    # 진행상활 로그 (너무 많으므로 100건단위)
                    if total_upsert_count % 500 == 0:
                        print(f"  ... {total_upsert_count}건 처리 중")
                        
            except Exception as e:
                print(f"[{market_gubun}] 처리 중 오류 발생: {e}")
                
        print(f"총 {total_upsert_count}개 종목 처리 완료")

    def run_batch(self):
        print("=" * 60)
        print("증권 종목 리스트 갱신 배치 시작 (pykrx)")
        print("=" * 60)
        
        # 1. 초기화 (use_yn = 'N')
        self.reset_all_stocks()
        
        # 2. 데이터 수집 및 업데이트
        self.update_stock_master()
        
        print("=" * 60)
        print("배치 작업 종료")
        print("=" * 60)

if __name__ == "__main__":
    updater = StockBatchUpdater()
    updater.run_batch()
