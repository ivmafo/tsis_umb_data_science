import duckdb
import os

db_path = "test_seq_persist.db"
if os.path.exists(db_path):
    os.remove(db_path)

def step1():
    print("--- Step 1: Init & Advance ---")
    con = duckdb.connect(db_path)
    con.execute("CREATE SEQUENCE s;")
    val = con.execute("SELECT nextval('s')").fetchone()[0]
    print(f"Conn 1: nextval -> {val}") # 1
    val = con.execute("SELECT nextval('s')").fetchone()[0]
    print(f"Conn 1: nextval -> {val}") # 2
    con.close()

def step2():
    print("--- Step 2: New Conn & Check ---")
    con = duckdb.connect(db_path)
    val = con.execute("SELECT nextval('s')").fetchone()[0]
    print(f"Conn 2: nextval -> {val}") # Should be 3
    con.close()

step1()
step2()
