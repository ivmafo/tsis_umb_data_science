from src.application.use_cases.get_time_stats import GetTimeStats
from src.application.use_cases.get_flight_type_stats import GetFlightTypeStats
import json

def verify_time_stats():
    print("Verifying Time Stats...")
    
    # 1. Test Time Stats (No filters)
    time_uc = GetTimeStats(db_path="data/metrics.duckdb")
    results = time_uc.execute({})
    print(f"Time Stats (No filters) Count: {len(results)}")
    if len(results) > 0:
        print("First 3 Time Stats:", results[:3])
    else:
        print("Time Stats returned empty!")

    # 2. Test Time Stats (Group by Year)
    results_year = time_uc.execute({"groupBy": "year"})
    print(f"Time Stats (Yearly) Count: {len(results_year)}")
    if len(results_year) > 0:
        print("First 3 Yearly Stats:", results_year[:3])

    # 3. Test Flight Type Stats
    type_uc = GetFlightTypeStats(db_path="data/metrics.duckdb")
    results_type = type_uc.execute({})
    print(f"Flight Type Stats Count: {len(results_type)}")
    if len(results_type) > 0:
        print("First 3 Types:", results_type[:3])

if __name__ == "__main__":
    verify_time_stats()
