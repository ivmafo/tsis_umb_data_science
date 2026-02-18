import duckdb
import os

db_path = "test_alter.db"
if os.path.exists(db_path):
    os.remove(db_path)

con = duckdb.connect(db_path)
con.execute("CREATE SEQUENCE s1 START 1;")
con.execute("CREATE TABLE t (id INTEGER DEFAULT nextval('s1'), val VARCHAR);")
con.execute("INSERT INTO t (val) VALUES ('A');") # id 1

# Create new sequence
con.execute("CREATE SEQUENCE s2 START 100;")

try:
    # Try to alter default
    con.execute("ALTER TABLE t ALTER id SET DEFAULT nextval('s2');")
    print("ALTER TABLE success")
    
    con.execute("INSERT INTO t (val) VALUES ('B');")
    res = con.execute("SELECT id, val FROM t WHERE val='B'").fetchone()
    print(f"Inserted: {res}")
    
except Exception as e:
    print(f"ALTER TABLE failed: {e}")

con.close()
