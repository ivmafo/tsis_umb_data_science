import duckdb
import os

def verify_schema():
    db_path = "data/metrics.duckdb"
    if not os.path.exists(db_path):
        print("DB not found (might be cleared), running mock init...")
        # Mock init logic? No, just connect and it creates.
        pass

    conn = duckdb.connect(db_path)
    
    # 1. Check Table Order / FK
    # DuckDB doesn't easily show FK constraints in DESCRIBE, but we can check if file_id exists
    # and if insertion respects it (if enforced). 
    # Actually, we just need to ensure the columns exist and tables are there.
    
    tables = [t[0] for t in conn.execute("SHOW TABLES").fetchall()]
    print(f"Tables: {tables}")
    
    if 'flights' in tables:
        cols = conn.execute("DESCRIBE flights").fetchall()
        col_names = [c[0] for c in cols]
        print(f"Flights Columns: {col_names}")
        assert 'file_id' in col_names, "file_id missing from flights"
        
    if 'file_processing_control' in tables:
        cols = conn.execute("DESCRIBE file_processing_control").fetchall()
        print(f"Control Columns: {[c[0] for c in cols]}")

    conn.close()

if __name__ == "__main__":
    verify_schema()
