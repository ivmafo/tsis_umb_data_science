import duckdb
import pandas as pd
import requests
import time
import os

API_URL = "http://localhost:8000/etl"
DB_PATH = "data/metrics.duckdb"
TEST_FILE = "data/test_integrity.csv"

def create_test_file():
    print(f"Creating test file: {TEST_FILE}")
    data = {
        "id": [999991, 999992],
        "fecha": ["2023-01-01", "2023-01-02"],
        "callsign": ["TEST01", "TEST02"]
    }
    df = pd.DataFrame(data)
    # Ensure directory exists
    os.makedirs("data", exist_ok=True)
    df.to_csv(TEST_FILE, index=False)

def trigger_ingestion():
    print("Triggering ingestion with force_reload=True...")
    res = requests.post(f"{API_URL}/ingest", params={"force_reload": True})
    print(f"Ingest Result: {res.json()}")
    
    # Wait for processing
    print("Waiting for processing...")
    timeout = 30
    for i in range(timeout):
        time.sleep(1)
        try:
            res = requests.get(f"{API_URL}/status")
            if res.status_code != 200:
                print(f"Status Check Failed: {res.status_code}")
                continue
            status = res.json()
            print(f"Status ({i}/{timeout}): {status}")
            
            # Wait until it's actually running? Or just wait until it's done?
            # If it starts idle (before BG task kicks in), we might exit too early.
            # Best to wait for "running" then "idle".
            
            # Simple logic: If we see progress > 0, we know it ran. 
            progress_str = status.get("progress", "0/0")
            processed, total = map(int, progress_str.split('/')) if '/' in progress_str else (0, 0)
            
            if status.get("status") == "idle" and processed > 0:
                 print("Ingestion verified as complete.")
                 break
        except Exception as e:
            print(f"Error checking status: {e}")

    else:
        print("Warning: Ingestion timed out or didn't finish cleanly.")

def verify_db():
    abs_db_path = os.path.abspath(DB_PATH)
    print(f"Verifying DB: {abs_db_path}")
    if not os.path.exists(abs_db_path):
        print(f"CRITICAL: DB File {abs_db_path} does not exist!")
        return

    try:
        conn = duckdb.connect(abs_db_path, read_only=True)
        
        # Check tables
        tables = conn.execute("SHOW TABLES").fetchall()
        print("Tables in DB:", tables)
        
        # 1. Verify Flights IDs match file (999991, 999992)
        flights = conn.execute("SELECT id, file_id, callsign FROM flights WHERE callsign LIKE 'TEST%' ORDER BY id").fetchall()
        print("Flights Found:", flights)
        
        expected_ids = [999991, 999992]
        found_ids = [f[0] for f in flights]
        
        if found_ids == expected_ids:
            print("SUCCESS: Flight IDs check passed (Inserted from File).")
        else:
            print(f"FAILURE: Flight IDs mismatch. Expected {expected_ids}, Got {found_ids}")
    
        # 2. Verify FK Integrity
        if not flights:
            print("FAILURE: No flights found to check FK.")
            return
    
        file_id_fk = flights[0][1]
        print(f"Checking FK file_id: {file_id_fk}")
        
        file_rec = conn.execute("SELECT id, file_name FROM file_processing_control WHERE id = ?", [file_id_fk]).fetchone()
        print("File Record Found:", file_rec)
        
        if file_rec and file_rec[1] == "test_integrity.csv":
            print("SUCCESS: Referential Integrity Check Passed.")
        else:
            print("FAILURE: Referential Integrity Check Failed.")
            
        # 3. Verify History Endpoint (as requested "verify history refresh")
        print("\nVerifying History Endpoint...")
        res = requests.get(f"{API_URL}/history")
        history = res.json()
        print(f"History Entries: {len(history)}")
        # Check if our file is in history
        found_in_history = any(h['file_name'] == 'test_integrity.csv' for h in history)
        if found_in_history:
             print("SUCCESS: History endpoint contains the processed file.")
        else:
             print("FAILURE: History endpoint does not show the file.")

        conn.close()
    except Exception as e:
        print(f"DB Error: {e}")

def cleanup():
    # Don't delete immediately so we can inspect if needed, or delete if success.
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)
        print("Test file removed.")

if __name__ == "__main__":
    try:
        create_test_file()
        trigger_ingestion()
        verify_db()
    finally:
        cleanup()
