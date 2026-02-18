import duckdb
import os

db_path = "test_repro_fix.db"
if os.path.exists(db_path):
    os.remove(db_path)

def init_db():
    con = duckdb.connect(db_path)
    con.execute("CREATE SEQUENCE IF NOT EXISTS seq;")
    con.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER DEFAULT nextval('seq'), name VARCHAR, PRIMARY KEY(id));")
    
    # Manual Insert
    con.execute("INSERT INTO items (id, name) VALUES (1, 'A') ON CONFLICT (id) DO NOTHING;")
    con.execute("INSERT INTO items (id, name) VALUES (2, 'B') ON CONFLICT (id) DO NOTHING;")
    
    # Try ALTER SEQUENCE
    try:
        # Get max id
        max_id = con.execute("SELECT MAX(id) FROM items").fetchone()[0]
        next_val = max_id + 1 if max_id else 1
        print(f"Max ID: {max_id}, Next Val: {next_val}")
        
        query = f"ALTER SEQUENCE seq RESTART WITH {next_val};"
        con.execute(query)
        print(f"ALTER SEQUENCE executed: {query}")
    except Exception as e:
        print(f"ALTER SEQUENCE failed: {e}")
    
    con.close()

def insert_new():
    con = duckdb.connect(db_path)
    try:
        res = con.execute("INSERT INTO items (name) VALUES ('C') RETURNING id;").fetchone()
        print(f"Inserted with ID: {res[0]}")
    except Exception as e:
        print(f"Insert failed: {e}")
    con.close()

print("--- First Run ---")
init_db()
insert_new()
