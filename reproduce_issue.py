import duckdb
from src.infrastructure.adapters.duckdb_airport_repository import DuckDBAirportRepository
import os

try:
    print("Initializing repository...")
    repo = DuckDBAirportRepository(db_path="tesis.db", csv_path="data/raw/data.csv")
    print("Repository initialized.")
    
    with duckdb.connect("tesis.db") as conn:
        print("Checking if table exists...")
        exists = conn.execute("SELECT count(*) FROM information_schema.tables WHERE table_name = 'airports'").fetchone()[0] > 0
        print(f"Table 'airports' exists: {exists}")
        
        if exists:
            count = conn.execute("SELECT count(*) FROM airports").fetchone()[0]
            print(f"Row count: {count}")
        else:
            print("Table does not exist!")

except Exception as e:
    print(f"Error occurred: {e}")
    import traceback
    traceback.print_exc()
