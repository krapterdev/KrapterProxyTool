import requests

BACKEND_URL = "http://localhost:8000"

def check_backend():
    print(f"Checking Backend at {BACKEND_URL}...")
    try:
        # Check Stats
        print("Fetching /stats...")
        res = requests.get(f"{BACKEND_URL}/stats", timeout=5)
        print(f"Stats Code: {res.status_code}")
        print(f"Stats Body: {res.text}")

        # Check Level 1
        print("Fetching /proxies/level1...")
        res = requests.get(f"{BACKEND_URL}/proxies/level1", timeout=5)
        print(f"Level 1 Code: {res.status_code}")
        print(f"Level 1 Body: {res.json()}")

    except Exception as e:
        print(f"❌ Error connecting to Backend: {e}")

if __name__ == "__main__":
    check_backend()
