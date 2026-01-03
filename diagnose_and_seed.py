import asyncio
import os
import random
import time
import psycopg2
from datetime import datetime

# Configuration
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/proxies")

print(f"🔌 Connecting to Database: {DB_URL}")

def get_db_connection():
    try:
        conn = psycopg2.connect(DB_URL)
        return conn
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        return None

def run_diagnostics():
    conn = get_db_connection()
    if not conn:
        return

    cursor = conn.cursor()
    
    # 1. Check Tables
    print("\n📊 Checking Tables...")
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    tables = cursor.fetchall()
    table_names = [t[0] for t in tables]
    print(f"   Found Tables: {table_names}")
    
    if 'proxies' not in table_names:
        print("❌ 'proxies' table MISSING! Run backend to init DB.")
        return

    # 2. Check Counts
    print("\n🔢 Current Data Counts:")
    cursor.execute("SELECT COUNT(*) FROM proxies")
    total = cursor.fetchone()[0]
    print(f"   Total Proxies: {total}")
    
    cursor.execute("SELECT level, COUNT(*) FROM proxies GROUP BY level")
    levels = cursor.fetchall()
    for lvl, count in levels:
        print(f"   - {lvl}: {count}")

    # 3. Force Seed
    print("\n💉 Injecting Dummy Data...")
    
    mock_proxies = []
    # Gold
    for i in range(10):
        mock_proxies.append({
            "ip": f"10.10.1.{i}", "port": "8080", "country": "United States", "code": "US",
            "latency": random.randint(50, 200), "level": "gold",
            "lat": random.uniform(30, 48), "lon": random.uniform(-120, -75)
        })
    # Silver
    for i in range(15):
        mock_proxies.append({
            "ip": f"10.10.2.{i}", "port": "3128", "country": "Germany", "code": "DE",
            "latency": random.randint(300, 700), "level": "silver",
            "lat": random.uniform(47, 55), "lon": random.uniform(6, 15)
        })
    # Bronze
    for i in range(20):
        mock_proxies.append({
            "ip": f"10.10.3.{i}", "port": "80", "country": "Brazil", "code": "BR",
            "latency": random.randint(1000, 5000), "level": "bronze",
            "lat": random.uniform(-30, -5), "lon": random.uniform(-70, -35)
        })

    added = 0
    for p in mock_proxies:
        proxy_str = f"{p['ip']}:{p['port']}:{p['country']}:{p['code']}"
        try:
            cursor.execute("""
                INSERT INTO proxies (proxy, ip, port, country, country_code, latency, level, last_checked, lat, lon)
                VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s, %s)
                ON CONFLICT (proxy) DO UPDATE SET
                    latency = EXCLUDED.latency,
                    level = EXCLUDED.level,
                    last_checked = CURRENT_TIMESTAMP,
                    lat = EXCLUDED.lat,
                    lon = EXCLUDED.lon
            """, (proxy_str, p['ip'], p['port'], p['country'], p['code'], p['latency'], p['level'], p['lat'], p['lon']))
            added += 1
        except Exception as e:
            print(f"   Error inserting {proxy_str}: {e}")

    conn.commit()
    print(f"✅ Successfully injected/updated {added} proxies.")
    
    # 4. Verify
    cursor.execute("SELECT COUNT(*) FROM proxies")
    new_total = cursor.fetchone()[0]
    print(f"   New Total: {new_total}")
    
    conn.close()

if __name__ == "__main__":
    run_diagnostics()
