import sys
import os
import duckdb
import logging

# Add src to path
sys.path.append(os.getcwd())

from src.application.use_cases.ingest_flights_data import IngestFlightsDataUseCase

# Configure logging to stdout
logging.basicConfig(level=logging.INFO)

def debug_reset():
    print("Debug Reset Database...")
    try:
        use_case = IngestFlightsDataUseCase(db_path="tesis.db", data_dir="data")
        
        # Manually connect and reset
        conn = duckdb.connect("tesis.db")
        
        print("Dropping tables...")
        conn.execute("DROP TABLE IF EXISTS flights")
        conn.execute("DROP TABLE IF EXISTS file_processing_control")
        conn.execute("DROP SEQUENCE IF EXISTS tracking_id_seq")
        
        print("Initializing DB...")
        use_case._init_db(conn)
        
        print("Verifying tables...")
        tables = conn.execute("SHOW TABLES").fetchall()
        print(f"Tables: {tables}")
        
        conn.close()
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_reset()
