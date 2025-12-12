import pymysql
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

class Database:
    def __init__(self):
        self.conn = None
        self.connect()

    def connect(self):
        """Connect to the MariaDB database"""
        try:
            self.conn = pymysql.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                db=DB_NAME,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True
            )
            print(f"Connected to MariaDB at {DB_HOST}:{DB_PORT}")
        except pymysql.MySQLError as e:
            print(f"Database Connection Error: {e}")
            self.conn = None

    def close(self):
        """Close the connection"""
        if self.conn:
            try:
                self.conn.close()
            except:
                pass
            self.conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def execute(self, query, args=None):
        """Execute a query (INSERT, UPDATE, DELETE)"""
        if not self.conn:
            self.connect()
            if not self.conn:
                return False
        
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, args)
            return True
        except pymysql.MySQLError as e:
            print(f"Query Error: {e}")
            return False

    def fetch_all(self, query, args=None):
        """Fetch all results (SELECT)"""
        if not self.conn:
            self.connect()
            if not self.conn:
                return []
        
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, args)
                return cursor.fetchall()
        except pymysql.MySQLError as e:
            print(f"Fetch Error: {e}")
            return []

    def fetch_one(self, query, args=None):
        """Fetch one result (SELECT)"""
        if not self.conn:
            self.connect()
            if not self.conn:
                return None
        
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, args)
                return cursor.fetchone()
        except pymysql.MySQLError as e:
            print(f"Fetch Error: {e}")
            return None
