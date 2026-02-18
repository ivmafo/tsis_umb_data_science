import sys
import os
import traceback

# Ensure src is in pythonpath
sys.path.append(os.getcwd())

try:
    from src.application.di.container import container
    from src.application.use_cases.predict_daily_demand import PredictDailyDemand
    from src.application.use_cases.predict_peak_hours import PredictPeakHours
    from src.application.use_cases.predict_airline_growth import PredictAirlineGrowth
    from src.application.use_cases.predict_sector_saturation import PredictSectorSaturation
except ImportError as e:
    print(f"CRITICAL IMPORT ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)

def test_prediction():
    print("--- Starting Predictive Module Debug ---")
    
    # 1. Check DB Path
    settings = container.config()
    db_path = settings.db_path
    print(f"Resolved DB Path: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"ERROR: Database file not found at {db_path}")
    else:
        print("Database file exists.")

    # 2. Daily Demand
    print("\n[TEST] Daily Demand...")
    try:
        use_case = container.predict_daily_demand_use_case()
        result = use_case.execute(days_ahead=5)
        print(f"SUCCESS: Retrieved {len(result.get('forecast', []))} forecast days.")
        print("Sample:", result.get('forecast', [])[:1])
    except Exception as e:
        print("FAILED Daily Demand:")
        traceback.print_exc()

    # 3. Peak Hours
    print("\n[TEST] Peak Hours...")
    try:
        use_case = container.predict_peak_hours_use_case()
        result = use_case.execute()
        print(f"SUCCESS: Retrieved heatmap data.")
    except Exception as e:
        print("FAILED Peak Hours:")
        traceback.print_exc()
        
    # 4. Airline Growth
    print("\n[TEST] Airline Growth...")
    try:
        use_case = container.predict_airline_growth_use_case()
        result = use_case.execute()
        print(f"SUCCESS: Retrieved growth data.")
    except Exception as e:
        print("FAILED Airline Growth:")
        traceback.print_exc()

    # 5. Sector Saturation
    print("\n[TEST] Sector Saturation...")
    try:
        use_case = container.predict_sector_saturation_use_case()
        # We need a sector ID. This might fail if no sectors exist, but let's try to just instantiate or check logic
        # For simplicity, we'll skip the execute if we don't have a sector ID, or just let it fail gracefully
        # But wait, looking at the code, it needs a sector_id.
        # Let's try to fetch sectors first if possible, or just skip.
        print("Skipping execution for saturation (needs specific sector ID). Instantiation was successful.")
    except Exception as e:
        print("FAILED Sector Saturation:")
        traceback.print_exc()

if __name__ == "__main__":
    test_prediction()
