import requests
import time

API_URL = "http://localhost:8000/etl/reset"

def test_reset_database():
    print(f"Testing reset database endpoint: {API_URL}")
    try:
        start_time = time.time()
        response = requests.post(API_URL)
        duration = time.time() - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("SUCCESS: Database reset endpoint works.")
        else:
            print("FAILURE: Database reset returned unexpected status.")
            
    except Exception as e:
        print(f"ERROR: Failed to connect to API. Is it running? {e}")

if __name__ == "__main__":
    test_reset_database()
