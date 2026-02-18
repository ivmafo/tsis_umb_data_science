
import requests
import time

def check_endpoints():
    base_url = "http://localhost:8000"
    max_retries = 5
    for i in range(max_retries):
        try:
            print(f"Attempt {i+1}...")
            resp = requests.get(f"{base_url}/filters/origins")
            if resp.status_code == 200:
                data = resp.json()
                print(f"Success! items count: {len(data)}")
                print(f"Sample: {data[:5]}")
                return
            else:
                print(f"Error: {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"Connection error: {e}")
        time.sleep(2)

if __name__ == "__main__":
    check_endpoints()
