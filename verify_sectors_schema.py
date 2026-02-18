
import duckdb

def verify_sectors_schema():
    db_path = "data/metrics.duckdb"
    conn = duckdb.connect(db_path)
    try:
        # Check if table exists
        tables = conn.execute("SHOW TABLES").fetchall()
        table_names = [t[0] for t in tables]
        if 'sectors' not in table_names:
            print("ERROR: Table 'sectors' does not exist.")
            return

        # Check columns
        columns = conn.execute("DESCRIBE sectors").fetchall()
        print("Table 'sectors' columns:")
        for col in columns:
            print(f"- {col[0]} ({col[1]})")

    except Exception as e:
        print(f"Error verifying schema: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    verify_sectors_schema()
