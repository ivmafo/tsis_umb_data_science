import duckdb
from src.application.di.container import container

def check_schema():
    settings = container.config()
    db_path = settings.db_path
    print(f"DB Path: {db_path}")
    
    conn = duckdb.connect(str(db_path), read_only=True)
    try:
        print("\n--- FLIGHTS TABLE SCHEMA ---")
        print(conn.execute("DESCRIBE flights").fetchdf())
        
        print("\n--- SAMPLE EMPRESA VALUES ---")
        print(conn.execute("SELECT empresa FROM flights LIMIT 10").fetchdf())
        
        print("\n--- DISTINCT EMPRESA ---")
        # Check if we can select distinct empresa, or if it crashes
        try:
            print(conn.execute("SELECT DISTINCT empresa FROM flights LIMIT 10").fetchdf())
        except Exception as e:
            print(f"Error fetching distinct empresa: {e}")

    except Exception as e:
        print(e)
    finally:
        conn.close()

if __name__ == "__main__":
    check_schema()
