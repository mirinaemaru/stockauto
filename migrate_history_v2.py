from db.database import Database

def migrate():
    db = Database()
    print("Migrating trading_history table...")
    
    queries = [
        "ALTER TABLE trading_history ADD COLUMN unit_price INT DEFAULT 0 COMMENT '매수/매도 단가'",
        "ALTER TABLE trading_history ADD COLUMN total_price INT DEFAULT 0 COMMENT '총 금액'",
        "ALTER TABLE trading_history ADD COLUMN profit_loss INT DEFAULT 0 COMMENT '손익'"
    ]
    
    for query in queries:
        try:
            print(f"Executing: {query}")
            db.execute(query)
        except Exception as e:
            print(f"Error (might already exist): {e}")
            
    print("Migration completed.")

if __name__ == "__main__":
    migrate()
