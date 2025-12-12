from db.database import Database
from trade import AutoTrader
import time

def verify_trading():
    db = Database()
    trader = AutoTrader()
    
    # 1. Insert Test Data
    print("Inserting test stock (Samsung Electronics: 005930)...")
    db.execute("DELETE FROM auto_stock WHERE stock_no = '005930'")
    db.execute("""
        INSERT INTO auto_stock (stock_no, use_yn, gubun, created_by) 
        VALUES ('005930', 'Y', 'TEST', 'system')
    """)
    
    # 2. Verify Buy Logic
    print("\n=== Testing Buy Logic ===")
    trader.buy_target_stocks()
    
    # Wait a bit
    time.sleep(2)
    
    # 3. Verify Sell Logic
    print("\n=== Testing Sell Logic ===")
    trader.sell_target_stocks()
    
    # 4. Clean up
    # db.execute("DELETE FROM auto_stock WHERE stock_no = '005930'")
    # print("\nTest data cleaned up.")

if __name__ == "__main__":
    verify_trading()
