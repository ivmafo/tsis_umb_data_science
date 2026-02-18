import sys
import os

# Ensure src is in pythonpath
sys.path.append(os.getcwd())

from src.infrastructure.adapters.duckdb_repository import DuckDBRegionRepository
from src.domain.entities.region import Region

print("--- Starting Repro Live ---")
try:
    repo = DuckDBRegionRepository(db_path="tesis.db")
    print("Repo initialized.")
    
    print("Checking existing regions:")
    regions = repo.get_all()
    for r in regions:
        print(f" - {r.id}: {r.name}")

    print("Attempting to create region...")
    new_reg = Region(name="ReproRegion", code="R_R", description="D", nivel_min=1)
    created = repo.create(new_reg)
    print(f"Created region: {created.id}")

except Exception as e:
    print("CAUGHT EXCEPTION:")
    print(e)
