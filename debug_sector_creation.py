
import duckdb
from src.application.use_cases.manage_sectors import ManageSectors
import json

db_path = "data/metrics.duckdb"

def debug_creation():
    uc = ManageSectors(db_path)
    
    payload = {
        "name": "DEBUG_SECTOR",
        "definition": {"origins": [], "destinations": []},
        "t_transfer": 0,
        "t_comm_ag": 0,
        "t_separation": 0,
        "t_coordination": 0,
        "adjustment_factor_r": 0.8,
        "capacity_baseline": 0
    }
    
    print("Attempting to create sector with payload:", payload)
    
    try:
        sector_id = uc.create(payload)
        print(f"Success! Sector created with ID: {sector_id}")
        
        # Verify it exists
        s = uc.get_by_id(sector_id)
        print("Retrieved sector:", s)
        
        # Cleanup
        uc.delete(sector_id)
        print("Cleanup successful")
        
    except Exception as e:
        print(f"Creation FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_creation()
