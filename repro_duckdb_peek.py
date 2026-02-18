import duckdb
import os

db_path = "test_repro_peek.db"
if os.path.exists(db_path):
    os.remove(db_path)

def init_db():
    con = duckdb.connect(db_path)
    con.execute("CREATE SEQUENCE IF NOT EXISTS seq;")
    con.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER DEFAULT nextval('seq'), name VARCHAR, PRIMARY KEY(id));")
    
    con.execute("INSERT INTO items (id, name) VALUES (1, 'A') ON CONFLICT (id) DO NOTHING;")
    
    try:
        # burn one
        con.execute("SELECT nextval('seq');")
        
        # Try to peek
        print("Peeking sequences:")
        res = con.execute("SELECT * FROM duckdb_sequences();").fetchall()
        print(res)
        
        # Try information_schema
        print("Peeking info schema:")
        res = con.execute("SELECT * FROM information_schema.sequences;").fetchall()
        print(res)

    except Exception as e:
        print(f"Peek failed: {e}")
    
    con.close()

init_db()
