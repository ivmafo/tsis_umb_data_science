
import duckdb

db_path = "data/metrics.duckdb"

def init_db():
    conn = duckdb.connect(db_path)
    try:
        # Create sectors table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sectors (
                id VARCHAR PRIMARY KEY,
                name VARCHAR,
                definition VARCHAR, -- JSON string
                t_transfer FLOAT,
                t_comm_ag FLOAT,
                t_separation FLOAT,
                t_coordination FLOAT,
                adjustment_factor_r FLOAT DEFAULT 0.8,
                capacity_baseline INTEGER
            );
        """)
        print("Table 'sectors' created or already exists.")
        
        # Verify
        print(conn.execute("DESCRIBE sectors").fetchall())
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
