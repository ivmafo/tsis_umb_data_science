from src.application.use_cases.get_flight_stats import GetFlightStats
from src.application.use_cases.get_destination_stats import GetDestinationStats
import json
from datetime import datetime

def verify_stats():
    print("Verifying Flight Stats...")
    
    # 1. Test Origin Stats (No filters)
    origin_uc = GetFlightStats(db_path="data/metrics.duckdb")
    results = origin_uc.execute({})
    print(f"Origin Stats (No filters) Count: {len(results)}")
    if len(results) > 0:
        print("Top 3 Origins:", results[:3])
    else:
        print("Origin Stats returned empty!")

    # 2. Test Destination Stats (No filters)
    dest_uc = GetDestinationStats(db_path="data/metrics.duckdb")
    results_dest = dest_uc.execute({})
    print(f"Destination Stats (No filters) Count: {len(results_dest)}")
    if len(results_dest) > 0:
        print("Top 3 Destinations:", results_dest[:3])

    # 3. Test with Date Filter
    # Assuming data exists in 2017 based on file names in data folder (e.g. 19_200217_210317.xlsx)
    filters_date = {
        "start_date": "2017-01-01",
        "end_date": "2017-12-31"
    }
    results_date = origin_uc.execute(filters_date)
    print(f"Origin Stats (2017) Count: {len(results_date)}")

if __name__ == "__main__":
    verify_stats()
