
import duckdb
from src.application.use_cases.manage_sectors import ManageSectors
from src.application.use_cases.calculate_sector_capacity import CalculateSectorCapacity
import json
import datetime

db_path = "data/metrics.duckdb"

def verify_full_flow():
    uc_manage = ManageSectors(db_path)
    uc_calc = CalculateSectorCapacity(db_path)
    
    # 1. Create Sector
    print("Creating sector for calculation test...")
    sector_data = {
        "name": "TEST_SECTOR_CALC",
        "definition": {"origins": ["SKBO"]}, # Assuming SKBO has flights
        "capacity_baseline": 30
    }
    sector_id = uc_manage.create(sector_data)
    print(f"Sector created: {sector_id}")
    
    try:
        # 2. Update with Manual Params
        print("Updating sector with manual params...")
        update_data = {
            "t_transfer": 30.0,
            "t_comm_ag": 45.0,
            "t_separation": 15.0,
            "t_coordination": 20.0,
            "adjustment_factor_r": 0.9
        }
        uc_manage.update(sector_id, update_data)
        
        # 3. Calculate Capacity
        print("Calculating capacity...")
        # Use a date range that covers the sample data seen in check_flights_data.py (2017-2018)
        filters = {
            "start_date": "2017-01-01",
            "end_date": "2018-12-31"
        }
        
        result = uc_calc.execute(sector_id, filters)
        print("Calculation Result:")
        print(json.dumps(result, indent=2))
        
        # Verify structure
        assert "SCV" in result
        assert "CH_Adjusted" in result
        assert result["TFC_Total"] == 30+45+15+20 # 110.0
        # Float precision check
        assert abs(result["R_Factor"] - 0.9) < 1e-6
        
        # Verify Formula usage (based on TFC and TPS)
        # SCV = TPS / (TFC * 1.3)
        tps = result["TPS"]
        tfc = result["TFC_Total"]
        expected_scv = tps / (tfc * 1.3)
        
        print(f"TPS: {tps}, TFC: {tfc}, SCV(Result): {result['SCV']}, SCV(Expected): {expected_scv}")
        
        # Allow small float diff
        assert abs(result["SCV"] - expected_scv) < 0.01
        
        print("\nVerification Successful: Calculation logic works as expected.")
        
    except Exception as e:
        print(f"Verification Failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        uc_manage.delete(sector_id)
        print("Test sector deleted.")

if __name__ == "__main__":
    verify_full_flow()
