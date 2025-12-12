from db.database import Database

def get_schema():
    db = Database()
    try:
        # Get Create Table statement
        result = db.fetch_one("SHOW CREATE TABLE stock_price_info")
        print(result['Create Table'])
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    get_schema()
