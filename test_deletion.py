import pandas as pd
import duckdb
import os
import shutil
from src.application.use_cases.ingest_flights_data import IngestFlightsDataUseCase

def verify_deletion():
    # Setup paths
    db_path = "test_deletion.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    data_dir = "test_data_del"
    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)
    os.makedirs(data_dir, exist_ok=True)
    
    filename = "to_delete.xlsx"
    file_path = os.path.join(data_dir, filename)

    # Create dummy data (CSV masquerading as XLSX for logic check? No, use CSV for simplicity if code allows, 
    # but controller forces .xlsx, UseCase processes based on extension? 
    # UseCase uses glob *.csv in original code but also supports xlsx?
    # Let's check code... UseCase supports both? It uses pandas/polars read_excel/read_csv based on ext.
    # Actually code showed read_excel for xlsx.
    # Let's make a CSV and rename to .csv for simplicity, or just use .csv if code supports it.
    # The list_files usually filters for .xlsx.
    # But `ingest` iterates `glob(os.path.join(self.data_dir, "*.xlsx"))`.
    # So I must make an xlsx.
    
    df = pd.DataFrame({"ID": [301], "SID": ["DEL1"], "Fecha": ["2023-12-01"]})
    df.to_excel(file_path, index=False)
    print(f"Created {file_path}")

    # Run Ingestion
    print("Ingesting...")
    use_case = IngestFlightsDataUseCase(db_path=db_path, data_dir=data_dir)
    use_case.execute(force_reload=True)

    # Verify Insertion
    conn = duckdb.connect(db_path)
    count = conn.execute("SELECT COUNT(*) FROM flights").fetchone()[0]
    print(f"Flights count: {count}")
    assert count > 0, "Ingestion failed"
    conn.close()

    # Verify Physical File exists
    assert os.path.exists(file_path), "File disappeared before deletion"

    # DELETE
    print("Deleting...")
    use_case.delete_file(filename)

    # Verify Deletion
    conn = duckdb.connect(db_path)
    count = conn.execute("SELECT COUNT(*) FROM flights").fetchone()[0]
    print(f"Flights count after delete: {count}")
    assert count == 0, "Flights not deleted"
    
    control_count = conn.execute("SELECT COUNT(*) FROM file_processing_control").fetchone()[0]
    print(f"Control count after delete: {control_count}")
    assert control_count == 0, "Control record not deleted"
    conn.close()

    # Verify Physical Deletion
    if not os.path.exists(file_path):
        print("SUCCESS: Physical file deleted.")
    else:
        print("FAILURE: Physical file still exists.")

    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)
    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)

if __name__ == "__main__":
    verify_deletion()
