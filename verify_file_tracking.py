import pandas as pd
import duckdb
import os
from src.application.use_cases.ingest_flights_data import IngestFlightsDataUseCase
from datetime import date

def verify_file_tracking():
    # Setup paths
    db_path = "test_verification.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    data_dir = "test_data"
    os.makedirs(data_dir, exist_ok=True)
    csv_path = os.path.join(data_dir, "file_tracking_test.csv")

    # Create dummy data
    data = {
        "ID": [201, 202],
        "SID": ["TEST1", "TEST2"],
        "Fecha": ["2023-11-01", "2023-11-02"],
        "Callsign": ["TRACK1", "TRACK2"]
    }
    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)

    print(f"Created test file at {csv_path}")

    # Run Ingestion
    print("Running ingestion...")
    use_case = IngestFlightsDataUseCase(db_path=db_path, data_dir=data_dir)
    result = use_case.execute(force_reload=True, specific_file=csv_path)
    print("Ingestion result:", result)

    # Verify Data
    conn = duckdb.connect(db_path)
    
    # 1. Check file_id column exists and is populated
    rows = conn.execute("SELECT id, file_id, sid FROM flights ORDER BY id").fetchall()
    print("\nRows inserted (id, file_id, sid):")
    for row in rows:
        print(row)

    # 2. Check relation to file_processing_control
    tracking_rows = conn.execute("SELECT id, file_name FROM file_processing_control").fetchall()
    print("\nTracking Control Rows (id, file_name):")
    for row in tracking_rows:
        print(row)

    try:
        file_id = rows[0][1]
        tracking_id = tracking_rows[0][0]
        assert file_id == tracking_id, f"File ID mismatch: Flight file_id={file_id}, Tracking ID={tracking_id}"
        print("\nSUCCESS: file_id links correctly to tracking table!")
    except Exception as e:
        print(f"\nFAILURE: {e}")

    conn.close()
    
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)
    if os.path.exists(csv_path):
        os.remove(csv_path)
    if os.path.exists(data_dir):
        os.rmdir(data_dir)

if __name__ == "__main__":
    verify_file_tracking()
