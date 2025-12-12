import time
import datetime
from db.database import Database
from kis_api import KisApi

class AutoTrader:
    def __init__(self):
        self.db = Database()
        self.kis = KisApi()

    def get_target_stocks(self):
        """Fetch stocks from auto_stock table where use_yn is 'Y'"""
        query = "SELECT stock_no, gubun FROM auto_stock WHERE use_yn = 'Y'"
        return self.db.fetch_all(query)

    def log_trade(self, stock_code, order_type, qty, result):
        """Log trade result to trading_history table"""
        result_code = ""
        result_msg = ""
        
        if isinstance(result, dict):
            result_code = result.get('rt_cd', '')
            result_msg = result.get('msg1', '')
        else:
            result_code = "ERROR"
            result_msg = str(result)
            
        # Default values for now (since we don't know execution price immediately)
        unit_price = 0
        total_price = 0
        profit_loss = 0
            
        query = """
            INSERT INTO trading_history (stock_no, order_type, qty, result_code, result_msg, unit_price, total_price, profit_loss)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.db.execute(query, (stock_code, order_type, qty, result_code, result_msg, unit_price, total_price, profit_loss))
        print(f"   [Log] Trade recorded: {order_type} {stock_code} (Code: {result_code})")

    def buy_target_stocks(self):
        print(f"\n[Buy Routine] Starting at {datetime.datetime.now()}")
        stocks = self.get_target_stocks()
        
        if not stocks:
            print("No target stocks found.")
            return

        for stock in stocks:
            stock_code = stock['stock_no']
            print(f"Processing Buy Order for {stock_code}...")
            
            # Buy 1 share as requested
            success, result = self.kis.buy(stock_code, qty=1)
            self.log_trade(stock_code, 'BUY', 1, result)
            
            if success:
                print(f"-> Buy Order Placed for {stock_code}")
            else:
                print(f"-> Buy Order Failed for {stock_code}")

    def sell_target_stocks(self):
        print(f"\n[Sell Routine] Starting at {datetime.datetime.now()}")
        stocks = self.get_target_stocks()
        
        if not stocks:
            print("No target stocks found.")
            return

        for stock in stocks:
            stock_code = stock['stock_no']
            print(f"Processing Sell Order for {stock_code}...")
            
            # Sell 1 share (assuming we bought 1)
            # Ideally we should check balance, but for this simple logic we try to sell 1.
            success, result = self.kis.sell(stock_code, qty=1)
            self.log_trade(stock_code, 'SELL', 1, result)
            
            if success:
                print(f"-> Sell Order Placed for {stock_code}")
            else:
                print(f"-> Sell Order Failed for {stock_code}")

    def run_scheduler(self):
        print("=== Auto Trading Scheduler Started ===")
        print("Waiting for 09:27 (Sell) or 15:11 (Buy)...")
        
        while True:
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M")
            
            # Check for Buy Time (15:11)
            if current_time == "15:11":
                # Ensure we only run once per minute
                if now.second < 5: 
                    self.buy_target_stocks()
                    time.sleep(60) # Sleep to avoid multiple runs within the same minute

            # Check for Sell Time (09:27)
            elif current_time == "09:27":
                if now.second < 5:
                    self.sell_target_stocks()
                    time.sleep(60)

            # Sleep for 1 second to check time frequently
            time.sleep(1)

if __name__ == "__main__":
    trader = AutoTrader()
    trader.run_scheduler()
