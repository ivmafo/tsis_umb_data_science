import duckdb
from src.infrastructure.adapters.duckdb_airport_repository import DuckDBAirportRepository
from src.domain.entities.airport import Airport

def verify_crud():
    print("Verifying CRUD operations on data/metrics.duckdb...")
    
    # 1. Setup Repository
    repo = DuckDBAirportRepository(db_path="data/metrics.duckdb", csv_path="data/raw/data.csv")
    
    # 2. Test CREATE
    print("\n--- Testing CREATE ---")
    new_airport = Airport(
        icao_code="TEST",
        iata_code="TST",
        name="Test Airport",
        city="Test City",
        country="Test Country",
        latitude=0.0,
        longitude=0.0,
        altitude=100,
        timezone=0,
        dst="U",
        type="small_airport",
        source="Test"
    )
    
    try:
        created = repo.create(new_airport)
        print(f"Created Airport ID: {created.id}")
        assert created.id is not None
    except Exception as e:
        print(f"CREATE FAILED: {e}")
        return

    airport_id = created.id

    # 3. Test READ (Get by ID)
    print("\n--- Testing READ ---")
    fetched = repo.get_by_id(airport_id)
    if fetched:
        print(f"Fetched: {fetched.name}, IC: {fetched.icao_code}")
        assert fetched.icao_code == "TEST"
    else:
        print("READ FAILED: Returned None")
        return

    # 4. Test UPDATE
    print("\n--- Testing UPDATE ---")
    fetched.name = "Updated Test Airport"
    updated = repo.update(fetched)
    if updated and updated.name == "Updated Test Airport":
        print(f"Update Successful: {updated.name}")
    else:
        print("UPDATE FAILED")

    # 5. Test DELETE
    print("\n--- Testing DELETE ---")
    deleted = repo.delete(airport_id)
    if deleted:
        print("Delete command successful")
        # Verify it's gone
        check = repo.get_by_id(airport_id)
        if check is None:
            print("Verification: Airport is truly gone.")
        else:
            print("DELETE FAILED: Airport still exists.")
    else:
        print("DELETE FAILED: Command returned False")

    # 6. Test LIST (Pagination)
    print("\n--- Testing LIST ---")
    items, total = repo.get_paginated(1, 5)
    print(f"Total Airports: {total}")
    print(f"Fetched {len(items)} items on page 1")
    assert len(items) > 0   

if __name__ == "__main__":
    verify_crud()
