
import duckdb

db_path = "data/metrics.duckdb"

try:
    conn = duckdb.connect(db_path)
    print(conn.execute("DESCRIBE flights").fetchall())
    # verify content of duracion
    print(conn.execute("SELECT duracion FROM flights LIMIT 5").fetchall())
    conn.close()
except Exception as e:
    print(f"Error: {e}")
