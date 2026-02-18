
import duckdb
import os
from src.application.di.container import get_manage_airports_use_case, get_manage_region_airports_use_case, container

def verify_unification():
    # 1. Verify Configuration
    db_path = container.config.provided.database_path()
    print(f"Target DB Path: {db_path}")
    assert "metrics.duckdb" in db_path, "Wrong DB Path configuration"

    # 2. Verify Airports Access
    print("Testing Airports Repository...")
    airport_uc = get_manage_airports_use_case()
    try:
        data, total = airport_uc.get_airports(1, 1)
        print(f"Airports Table Accessible. Total rows: {total}")
    except Exception as e:
        print(f"Airports Error: {e}")
        # If table doesn't exist yet, it should have been created by _init_db inside the repo init.
        # Check if table exists in the file.
        conn = duckdb.connect(db_path)
        try:
            tables = conn.execute("SHOW TABLES").fetchall()
            print(f"Tables in {db_path}: {tables}")
        finally:
            conn.close()
        raise e

    # 3. Verify Region Airports Access
    print("Testing Region Airports Repository...")
    ra_uc = get_manage_region_airports_use_case()
    try:
        data, total = ra_uc.get_region_airports(1, 1)
        print(f"RegionAirports Table Accessible. Total rows: {total}")
    except Exception as e:
        print(f"RegionAirports Error: {e}")
        raise e

    print("SUCCESS: All repositories are using the unified database.")

if __name__ == "__main__":
    verify_unification()
