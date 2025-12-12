from db.database import Database

def check_history():
    db = Database()
    print("Fetching trading history...")
    rows = db.fetch_all("SELECT * FROM trading_history ORDER BY id DESC LIMIT 5")
    
    for row in rows:
        print(row)

if __name__ == "__main__":
    check_history()
