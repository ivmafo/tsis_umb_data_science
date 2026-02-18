
import duckdb
import requests
import json

def check_data():
    db_path = "data/metrics.duckdb"
    conn = duckdb.connect(db_path, read_only=True)
    try:
        # Check flights count
        count = conn.execute("SELECT count(*) FROM flights").fetchone()[0]
        print(f"Total flights in DB: {count}")
        
        if count > 0:
            # Check sample origins
            origins = conn.execute("SELECT DISTINCT origen FROM flights LIMIT 5").fetchall()
            print(f"Sample origins: {origins}")
    except Exception as e:
        print(f"DB Error: {e}")
    finally:
        conn.close()

def test_endpoints():
    base_url = "http://localhost:8000"
    try:
        # Test Origins
        print("\nTesting /filters/origins...")
        resp = requests.get(f"{base_url}/filters/origins")
        print(f"Status: {resp.status_code}")
        try:
            data = resp.json()
            print(f"Data type: {type(data)}")
            print(f"Data sample (first 3): {data[:3] if isinstance(data, list) else data}")
        except:
             print(f"Raw response: {resp.text}")

        # Test Save Sector (Create)
        print("\nTesting POST /sectors/...")
        payload = {
            "name": "Test Sector Debug",
            "definition": {"origins": ["SKBO"], "destinations": ["SKRG"]},
            "t_transfer": 10,
            "t_comm_ag": 10,
            "t_separation": 5,
            "t_coordination": 5,
            "adjustment_factor_r": 0.8,
            "capacity_baseline": 30
        }
        resp = requests.post(f"{base_url}/sectors/", json=payload)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")

    except Exception as e:
        print(f"Request Error: {e}")

if __name__ == "__main__":
    check_data()
    test_endpoints()
