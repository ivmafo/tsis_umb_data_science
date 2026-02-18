import duckdb
import os

db_path = "test_repro.db"
if os.path.exists(db_path):
    os.remove(db_path)

def init_db():
    con = duckdb.connect(db_path)
    con.execute("CREATE SEQUENCE IF NOT EXISTS seq;")
    con.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER DEFAULT nextval('seq'), name VARCHAR, PRIMARY KEY(id));")
    
    # Manual Insert
    con.execute("INSERT INTO items (id, name) VALUES (1, 'A') ON CONFLICT (id) DO NOTHING;")
    con.execute("INSERT INTO items (id, name) VALUES (2, 'B') ON CONFLICT (id) DO NOTHING;")
    
    # Try setval
    try:
        con.execute("SELECT setval('seq', (SELECT MAX(id) FROM items));")
        print("Setval executed")
    except Exception as e:
        print(f"Setval failed: {e}")
    
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

print("\n--- Second Run (Simulate Restart) ---")
init_db()
insert_new()
