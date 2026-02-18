
import duckdb
from src.application.use_cases.manage_sectors import ManageSectors
import json

db_path = "data/metrics.duckdb"

def verify_sector_update():
    uc = ManageSectors(db_path)
    
    # 1. Create Sector
    print("Creating sector...")
    sector_data = {
        "name": "TEST_SECTOR_MANUAL",
        "definition": {"origins": ["SKBO"]},
        "capacity_baseline": 30
    }
    sector_id = uc.create(sector_data)
    print(f"Sector created with ID: {sector_id}")
    
    # 2. Update with Manual params
    print("Updating sector with manual params...")
    update_data = {
        "t_transfer": 10.0,
        "t_comm_ag": 20.0,
        "t_separation": 5.0,
        "t_coordination": 15.0,
        "adjustment_factor_r": 0.85
    }
    # Note: dictionary keys must match what update expects. The controller converts pydantic to dict.
    # ManageSectors.update expects dict keys that match column names.
    pk = uc.update(sector_id, update_data)
    print(f"Update success: {pk}")
    
    # 3. specific Verify
    updated_sector = uc.get_by_id(sector_id)
    print("Updated Sector Data:")
    print(updated_sector)
    
    assert updated_sector['t_transfer'] == 10.0
    assert updated_sector['t_comm_ag'] == 20.0
    assert abs(updated_sector['adjustment_factor_r'] - 0.85) < 1e-6
    
    print("\nVerification Successful: Manual parameters persisted.")
    
    # Cleanup
    uc.delete(sector_id)
    print("Test sector deleted.")

if __name__ == "__main__":
    verify_sector_update()
