import sys
import os
import logging
import duckdb

# Add src to path
sys.path.append(os.getcwd())

from src.application.use_cases.ingest_flights_data import IngestFlightsDataUseCase

# Configure logging to stdout
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_ingest():
    print("Debug Ingestion Direct...")
    db_path = "data/metrics.duckdb"
    
    # 1. Check DB before
    con = duckdb.connect(db_path)
    try:
        count_before = con.execute("SELECT count(*) FROM flights").fetchone()[0]
        print(f"Rows before: {count_before}")
    except:
        print("Table flights likely doesn't exist.")

    use_case = IngestFlightsDataUseCase(db_path=db_path, data_dir="data")
    
    # 2. Run Ingestion
    print("Running execute(force_reload=True)...")
    result = use_case.execute(force_reload=True)
    print(f"Result: {result}")
    
    # 3. Check DB after
    try:
        count_after = con.execute("SELECT count(*) FROM flights").fetchone()[0]
        print(f"Rows after: {count_after}")
    except Exception as e:
        print(f"Error checking after: {e}")
        
    con.close()

if __name__ == "__main__":
    debug_ingest()
