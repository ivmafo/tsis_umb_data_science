import json
import sys
import os

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from src.application.use_cases.predict_daily_demand import PredictDailyDemand
    from src.application.use_cases.predict_peak_hours import PredictPeakHours
except ImportError as e:
    print(f"CRITICAL IMPORT ERROR: {e}", flush=True)
    sys.exit(1)

def inspect_responses():
    print("--- Inspecting Backend Responses ---", flush=True)
    
    # 1. Daily Demand
    print("\n[1] Testing PredictDailyDemand...")
    try:
        dd_use_case = PredictDailyDemand("data/metrics.duckdb")
        result = dd_use_case.execute(days_ahead=5)
        
        if "executive_report" in result:
            print("[OK] 'executive_report' FOUND in Daily Demand response.")
            print("Title:", result['executive_report'].get('title'))
        else:
            print("[FAIL] 'executive_report' MISSING in Daily Demand response.")
            print("Keys found:", list(result.keys()))
    except Exception as e:
        print(f"Error testing Daily Demand: {e}")

    # 2. Peak Hours
    print("\n[2] Testing PredictPeakHours...")
    try:
        ph_use_case = PredictPeakHours("data/metrics.duckdb")
        result = ph_use_case.execute()
        
        if "executive_report" in result:
            print("[OK] 'executive_report' FOUND in Peak Hours response.")
            print("Title:", result['executive_report'].get('title'))
        else:
            print("[FAIL] 'executive_report' MISSING in Peak Hours response.")
            print("Keys found:", list(result.keys()))
    except Exception as e:
        print(f"Error testing Peak Hours: {e}")

    # 3. Airline Growth
    try:
        from src.application.use_cases.predict_airline_growth import PredictAirlineGrowth
        ag_use_case = PredictAirlineGrowth("data/metrics.duckdb")
        result = ag_use_case.execute()
        
        if "executive_report" in result:
            print("[OK] 'executive_report' FOUND in Airline Growth response.")
            print("Title:", result['executive_report'].get('title'))
        else:
            print("[FAIL] 'executive_report' MISSING in Airline Growth response.")
    except Exception as e:
        print(f"Error testing Airline Growth: {e}")

    # 4. Sector Saturation
    try:
        from src.application.use_cases.predict_sector_saturation import PredictSectorSaturation
        # Need a mock demand result for saturation
        mock_demand = {"forecast": [{"value": 100}]} 
        ss_use_case = PredictSectorSaturation("data/metrics.duckdb")
        # We need a valid sector_id, let's try to get one or use a dummy if the code handles it
        # Inspecting the code, it needs a real sector or we mock the DB. 
        # For simplicity, we'll try to run it. If it fails due to DB, we'll know.
        # However, PredictSectorSaturation.execute takes (sector_id, demand_result).
        # We might need to mock the db connection or use a real one.
        # Let's assume we can pass a dummy sector_id and it might fail on DB lookup if not found.
        # But wait, I can just check the code of PredictSectorSaturation to see if it needs a valid sector.
        # It queries the DB for sector details.
        pass # Skipping complex setup for now, let's check code first.
        # Actually, let's try to run it with a potential sector_id if possible, or just skip if too hard.
        # Better: let's rely on reading the code for now for Saturation/Seasonal if this script is too complex to setup.
    except Exception as e:
        print(f"Error testing Sector Saturation: {e}")

    # 5. Seasonal Trend
    print("\n[5] Testing PredictSeasonalTrend...")
    try:
        from src.application.use_cases.predict_seasonal_trend import PredictSeasonalTrend
        st_use_case = PredictSeasonalTrend("data/metrics.duckdb")
        result = st_use_case.execute(start_date="2023-01-01", end_date="2023-12-31")
        
        if "executive_report" in result:
            print("[OK] 'executive_report' FOUND in Seasonal Trend response.")
            print("Title:", result['executive_report'].get('title'))
        else:
            print("[FAIL] 'executive_report' MISSING in Seasonal Trend response.")
            if "metrics" in result and "executive_report" in result["metrics"]:
                 print("[INFO] Found 'executive_report' inside 'metrics' object.")
            else:
                 print("Keys found:", list(result.keys()))
    except Exception as e:
        print(f"Error testing Seasonal Trend: {e}")

if __name__ == "__main__":
    inspect_responses()
