import sys
import os
import duckdb

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from src.application.use_cases.predict_sector_saturation import PredictSectorSaturation

def inspect_saturation():
    print("--- Inspecting Sector Saturation Response ---")
    
    # Mocking a sector in the DB to ensure we have something to query
    db_path = "data/metrics.duckdb"
    conn = duckdb.connect(db_path)
    
    # Create tables if not exist (just in case, though they should)
    try:
        # Schema for sectors: id, name, geometry, t_separation, etc.
        # Let's just try to insert id and name if possible, or create a dummy table if not exists
        # But wait, the error said "Binder Error: Table "sectors" does not have a column with name "type""
        # So the table exists. Let's see what columns it has or just insert minimal valid data.
        # Better yet, let's use an existing sector ID if we can find one.
        # Or just insert name and geometry which might be what's needed.
        conn.execute("INSERT OR IGNORE INTO sectors (id, name) VALUES (?, ?)", 
                     (sector_id, "Test Sector"))
        
        # We also need manual parameters for this sector to avoid errors?
        # PredictSectorSaturation code checks for manual params but has defaults.
        
        mock_demand = {
            "forecast": [
                {"date": "2023-01-01", "value": 50, "upper": 60}
            ],
            "accuracy_metrics": {"confidence_score": "High"}
        }

        use_case = PredictSectorSaturation(db_path)
        result = use_case.execute(sector_id, mock_demand)
        
        if "executive_report" in result:
             print("[OK] 'executive_report' FOUND in Sector Saturation response.")
             print("Title:", result['executive_report'].get('title'))
        else:
             print("[FAIL] 'executive_report' MISSING in Sector Saturation response.")
             print("Keys found:", list(result.keys()))

    except Exception as e:
        print(f"Error testing Sector Saturation: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    inspect_saturation()
