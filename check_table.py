from db.database import Database

def check_table():
    db = Database()
    try:
        print("Checking if table 'stock_price_info' exists...")
        rows = db.fetch_all("SHOW TABLES LIKE 'stock_price_info'")
        if rows:
            print("Table 'stock_price_info' EXISTS.")
            # Show columns
            desc = db.fetch_all("DESCRIBE stock_price_info")
            print(f"Columns: {[row['Field'] for row in desc]}")
        else:
            print("Table 'stock_price_info' does NOT exist.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_table()
