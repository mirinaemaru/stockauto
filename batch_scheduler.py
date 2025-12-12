import time
import datetime
from batch_update_stocks import StockBatchUpdater

class BatchScheduler:
    def __init__(self):
        self.batch_time = "08:00"  # 매일 오전 8시에 실행
        
    def run_scheduler(self):
        print("=" * 60)
        print("배치 스케줄러 시작")
        print(f"실행 시간: 매일 {self.batch_time}")
        print("=" * 60)
        
        while True:
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M")
            
            if current_time == self.batch_time:
                if now.second < 5:  # 중복 실행 방지
                    print(f"\n[{now.strftime('%Y-%m-%d %H:%M:%S')}] 배치 작업 시작")
                    
                    try:
                        updater = StockBatchUpdater()
                        updater.run_batch()
                    except Exception as e:
                        print(f"배치 작업 중 오류 발생: {e}")
                    
                    print(f"다음 실행 예정: 내일 {self.batch_time}\n")
                    time.sleep(60)  # 1분 대기
            
            time.sleep(1)

if __name__ == "__main__":
    scheduler = BatchScheduler()
    scheduler.run_scheduler()
