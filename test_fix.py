import duckdb
import os
import shutil
from src.infrastructure.adapters.duckdb_repository import DuckDBRegionRepository
from src.domain.entities.region import Region

db_path = "test_fix_verify.db"
if os.path.exists(db_path):
    os.remove(db_path)

print("--- Step 1: Initialize DB and verify manual seeds ---")
# This triggers _init_db which creates the table and seeds ID 1 and 2
repo = DuckDBRegionRepository(db_path=db_path)

regions = repo.get_all()
print(f"Initial regions count: {len(regions)}") # Should be 2
for r in regions:
    print(f" - {r.id}: {r.name}")

print("\n--- Step 2: Create new region (Should use ID 3) ---")
new_region = Region(
    name="Test Region",
    code="TEST",
    description="Test Desc",
    nivel_min=1
)

try:
    created = repo.create(new_region)
    print(f"Successfully created region with ID: {created.id}")
except Exception as e:
    print(f"FAILED to create region: {e}")

print("\n--- Step 3: Simulate Restart & create another ---")
# Re-instantiate repo to trigger _init_db again (which runs the sync logic)
repo2 = DuckDBRegionRepository(db_path=db_path)
new_region_2 = Region(
    name="Test Region 2",
    code="TEST2",
    description="Test Desc 2",
    nivel_min=1
)

try:
    created2 = repo2.create(new_region_2)
    print(f"Successfully created region 2 with ID: {created2.id}")
except Exception as e:
    print(f"FAILED to create region 2: {e}")
