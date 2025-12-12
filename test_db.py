from db.database import Database
import sys

def test_connection():
    print("Testing MariaDB connection...")
    db = Database()
    if db.conn:
        print("SUCCESS: Connected to database!")
        
        # Try a simple query
        try:
            version = db.fetch_one("SELECT VERSION() as version")
            print(f"Database Version: {version['version']}")
        except Exception as e:
            print(f"Query Warning: {e}")
            
        db.close()
        return True
    else:
        print("FAILURE: Could not connect to database.")
        print("Please check your settings in secrets.py and ensure MariaDB is running.")
        return False

if __name__ == "__main__":
    if test_connection():
        sys.exit(0)
    else:
        sys.exit(1)
