import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def check_seasonal_trend():
    print("\n--- Checking Seasonal Trend ---")
    # Simulation of default params or user actions
    # Requires start_date and end_date
    params = {
        "start_date": "2023-01-01",
        "end_date": "2023-12-31"
    }
    try:
        url = f"{BASE_URL}/predictive/seasonal-trend"
        print(f"GET {url} with params {params}")
        resp = requests.get(url, params=params)
        if resp.status_code != 200:
            print(f"❌ Error {resp.status_code}: {resp.text}")
            return
        
        data = resp.json()
        if 'executive_report' in data:
            print("FOUND: Executive Report in Seasonal Trend")
            print("Title:", data['executive_report'].get('title'))
        else:
            print("MISSING: Executive Report in Seasonal Trend")
            print("Keys:", data.keys())
            if 'metrics' in data:
                print("Metrics keys:", data['metrics'].keys())
                if 'executive_report' in data['metrics']:
                     print("FOUND: But found in metrics.executive_report")
                else:
                     print("MISSING: Not found in metrics either.")

    except Exception as e:
        print(f"Exception: {e}")

def check_peak_hours():
    print("\n--- Checking Peak Hours ---")
    
    # Case 1: No params (Default)
    try:
        url = f"{BASE_URL}/predictive/peak-hours"
        print(f"GET {url} (No params)")
        resp = requests.get(url)
        if resp.status_code != 200:
            print(f"Error {resp.status_code}: {resp.text}")
        else:
            data = resp.json()
            if 'executive_report' in data:
                 print("FOUND: Executive Report (No params)")
            elif 'metrics' in data and 'executive_report' in data['metrics']:
                 print("FOUND: Executive Report in metrics (No params)")
            else:
                 print("MISSING: Executive Report (No params)")
    except Exception as e:
        print(f"Exception: {e}")

    # Case 2: With Dates
    try:
        params = {
            "start_date": "2023-01-01",
            "end_date": "2023-01-31"
        }
        print(f"GET {url} with params {params}")
        resp = requests.get(url, params=params)
        if resp.status_code != 200:
            print(f"Error {resp.status_code}: {resp.text}")
        else:
            data = resp.json()
            if 'executive_report' in data:
                 print("FOUND: Executive Report (With Date Params)")
            elif 'metrics' in data and 'executive_report' in data['metrics']:
                 print("FOUND: Executive Report in metrics (With Date Params)")
            else:
                 print("MISSING: Executive Report (With Date Params)")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    check_seasonal_trend()
    check_peak_hours()
