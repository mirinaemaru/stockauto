from db.database import Database
import os

def init_db():
    db = Database()
    schema_path = os.path.join(os.path.dirname(__file__), 'db', 'schema.sql')
    
    print(f"Reading schema from {schema_path}...")
    try:
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
            
        # Split by ; to handle multiple statements if any (though we only have one now)
        statements = schema_sql.split(';')
        
        for statement in statements:
            if statement.strip():
                print(f"Executing: {statement.strip()[:50]}...")
                db.execute(statement)
                
        print("Database initialization completed.")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
