
import duckdb

def describe_flights():
    db_path = "data/metrics.duckdb"
    conn = duckdb.connect(db_path, read_only=True)
    try:
        columns = conn.execute("DESCRIBE flights").fetchall()
        print("Table 'flights' columns:")
        for col in columns:
            print(f"- {col[0]}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    describe_flights()
