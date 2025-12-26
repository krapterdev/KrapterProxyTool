import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "backend", "proxies.db")

def check_data():
    if not os.path.exists(DB_FILE):
        print(f"❌ Database file not found at: {DB_FILE}")
        return

    print(f"Checking database: {DB_FILE}")
    
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # List tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tables:", [t["name"] for t in tables])

        cursor.execute("SELECT * FROM proxies")
        rows = cursor.fetchall()
        
        print(f"Total Proxies: {len(rows)}")
        
        malformed_count = 0
        for row in rows:
            proxy = row["proxy"]
            latency = row["latency"]
            country = row["country"]
            country_code = row["country_code"]
            level = row["level"]
            
            is_valid = True
            
            # Check 1: Proxy format (IP:PORT:COUNTRY:CODE)
            # Note: The code in dashboard.html expects IP:PORT:COUNTRY:CODE or at least IP:PORT
            parts = proxy.split(":")
            if len(parts) < 2:
                print(f"Malformed Proxy String: '{proxy}'")
                is_valid = False
            
            # Check 2: Latency
            if not isinstance(latency, int):
                 print(f"Invalid Latency: {latency} for proxy {proxy}")
                 is_valid = False
                 
            # Check 3: Level
            if level not in ["gold", "silver", "bronze"]:
                print(f"Invalid Level: '{level}' for proxy {proxy}")
                is_valid = False

            if not is_valid:
                malformed_count += 1

        if malformed_count == 0:
            print("No malformed entries found.")
        else:
            print(f"Found {malformed_count} malformed entries.")
            
        conn.close()
        
    except Exception as e:
        print(f"Error accessing database: {e}")

if __name__ == "__main__":
    check_data()
