
import duckdb

db_path = "data/metrics.duckdb"

try:
    conn = duckdb.connect(db_path)
    print(conn.execute("DESCRIBE sectors").fetchall())
    conn.close()
except Exception as e:
    print(f"Error: {e}")
