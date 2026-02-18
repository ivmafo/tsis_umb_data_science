from src.infrastructure.adapters.duckdb_airport_repository import DuckDBAirportRepository
from src.application.use_cases.manage_airports import ManageAirports
from src.domain.entities.airport import Airport
import json

try:
    print("Testing API logic...")
    # Use the correct DB path
    repo = DuckDBAirportRepository(db_path="data/metrics.duckdb", csv_path="data/raw/data.csv")
    use_case = ManageAirports(repo)
    
    print("Calling get_airports...")
    items, total = use_case.get_airports(page=1, page_size=10, search="")
    
    print(f"Total: {total}")
    print(f"Items count: {len(items)}")
    
    if len(items) > 0:
        print("First item sample:")
        print(items[0].model_dump())
        
        # Verify it matches expected fields in controller
        # id, icao_code, iata_code, name, city, country, latitude, longitude, altitude, timezone, dst, type, source
        required_fields = ["id", "icao_code", "iata_code", "name", "city", "country", 
                          "latitude", "longitude", "altitude", "timezone", "dst", "type", "source"]
        
        item_dict = items[0].model_dump()
        missing = [f for f in required_fields if f not in item_dict]
        if missing:
            print(f"MISSING FIELDS: {missing}")
        else:
            print("All required fields presence check passed.")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
