from src.infrastructure.adapters.duckdb_repository import DuckDBRegionRepository
from src.domain.entities.region import Region
import sys
import os

# Ensure src is in python path
sys.path.append(os.getcwd())

def test_create_region():
    print("--- Starting Reproduction Script ---")
    db_path = "tesis.db"
    
    if not os.path.exists(db_path):
        print(f"Warning: {db_path} does not exist. A new one will be created.")
    
    repo = DuckDBRegionRepository(db_path=db_path)
    
    print("Listing existing regions...")
    try:
        regions = repo.get_all()
        print(f"Found {len(regions)} regions.")
        for r in regions:
            print(f" - ID: {r.id}, Name: {r.name}")
            
        max_id = max([r.id for r in regions]) if regions else 0
        print(f"Max ID found: {max_id}")
    except Exception as e:
        print(f"Error listing regions: {e}")
        return

    print("\nAttempting to create a new region...")
    new_region = Region(
        name="Test Region Debug",
        code="TEST-DBG",
        description="A test region used for debugging sequence",
        nivel_min=100
    )

    try:
        created = repo.create(new_region)
        print(f"SUCCESS: Created region with ID: {created.id}")
    except Exception as e:
        print(f"FAILURE: Could not create region.")
        print(f"Error details: {e}")

if __name__ == "__main__":
    test_create_region()
