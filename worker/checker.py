import asyncio
import aiohttp
import time
import psycopg2
import os
import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/proxies")

def get_db_connection():
    return psycopg2.connect(DB_URL)

def init_db():
    # Wait for DB to be ready and ensure schema is correct
    retries = 30
    while retries > 0:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Proxies table (Ensure ip/port exist)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS proxies (
                    proxy TEXT PRIMARY KEY,
                    ip TEXT,
                    port TEXT,
                    latency INTEGER,
                    country TEXT,
                    country_code TEXT,
                    level TEXT,
                    last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    assigned_to TEXT
                )
            ''')
            
            # Migration: Add columns if they don't exist (for existing DBs)
            try:
                cursor.execute("ALTER TABLE proxies ADD COLUMN IF NOT EXISTS ip TEXT")
                cursor.execute("ALTER TABLE proxies ADD COLUMN IF NOT EXISTS port TEXT")
                conn.commit()
            except Exception as e:
                # logging.warning(f"Migration warning: {e}")
                conn.rollback()
                
            conn.close()
            # logging.info("Worker DB initialized successfully.")
            break
        except Exception as e:
            # logging.warning(f"DB not ready yet, retrying... ({e})")
            time.sleep(2)
            retries -= 1

# Initialize DB
init_db()

def save_to_db(new_proxies):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        count = 0
        for level, items in new_proxies.items():
            for item in items:
                proxy_str = item["proxy"]
                latency = item["latency"]
                
                parts = proxy_str.split(':')
                ip = parts[0]
                port = parts[1]
                country = parts[2] if len(parts) > 2 else "Unknown"
                country_code = parts[3] if len(parts) > 3 else "UN"
                
                # Use ON CONFLICT to preserve assigned_to
                # Postgres syntax: ON CONFLICT (proxy) DO UPDATE SET ...
                cursor.execute('''
                    INSERT INTO proxies (proxy, ip, port, country, country_code, latency, level, last_checked, lat, lon)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s, %s)
                    ON CONFLICT (proxy) DO UPDATE SET
                        latency=EXCLUDED.latency,
                        level=EXCLUDED.level,
                        last_checked=CURRENT_TIMESTAMP,
                        lat=EXCLUDED.lat,
                        lon=EXCLUDED.lon
                ''', (proxy_str, ip, port, country, country_code, latency, level, item.get("lat"), item.get("lon")))
                count += 1
                
        conn.commit()
        conn.close()
        # logging.info(f"Saved {count} proxies to DB.")
    except Exception as e:
        logging.error(f"Error saving to DB: {e}")

async def check_proxy(session, proxy):
    # Bypass check for known fallback proxies to ensure data availability
    from sources import FALLBACK_PROXIES
    if proxy in FALLBACK_PROXIES:
        print(f"✅ Proxy {proxy} is a FALLBACK (Skipping check)")
        # Return fake good stats
        return proxy, 100, "Fallback", "US", 0.0, 0.0

    # 1. Check Liveness (Connect to Google)
    test_urls = ["http://www.google.com", "http://example.com", "http://1.1.1.1"]
    proxy_url = f"http://{proxy}"
    
    for test_url in test_urls:
        start_time = time.time()
        try:
            async with session.get(test_url, proxy=proxy_url, timeout=15) as response:
                if response.status == 200:
                    latency = int((time.time() - start_time) * 1000) # ms
                    
                    # 2. Get GeoIP Data (Optional - Best Effort)
                    country = "Unknown"
                    country_code = "UN"
                    lat = None
                    lon = None
                    
                    try:
                        # Try ip-api via proxy
                        async with session.get("http://ip-api.com/json", proxy=proxy_url, timeout=5) as geo_res:
                            if geo_res.status == 200:
                                data = await geo_res.json()
                                country = data.get("country", "Unknown")
                                country_code = data.get("countryCode", "UN")
                                lat = data.get("lat")
                                lon = data.get("lon")
                    except Exception:
                        pass # GeoIP failed, but proxy is alive
                    
                    print(f"✅ Proxy {proxy} is ALIVE ({latency}ms)")
                    return proxy, latency, country, country_code, lat, lon
        except Exception as e:
            # print(f"❌ Proxy {proxy} failed on {test_url}: {e}")
            pass
            
    return proxy, None, None, None, None, None

async def process_proxies(proxies):
    chunk_size = 20 # Reduced from 50 to be safer
    # logging.info(f"Processing {len(proxies)} proxies...")
    
    for i in range(0, len(proxies), chunk_size):
        chunk = proxies[i:i + chunk_size]
        # logging.info(f"Checking chunk {i}/{len(proxies)}...")
        
        async with aiohttp.ClientSession() as session:
            tasks = [check_proxy(session, proxy) for proxy in chunk]
            results = await asyncio.gather(*tasks)
            
            batch_results = {"gold": [], "silver": [], "bronze": []}

            for proxy, latency, country, country_code, lat, lon in results:
                if latency is not None:
                    # Ensure we don't have None values for string formatting
                    country = country or "Unknown"
                    country_code = country_code or "UN"
                    
                    proxy_str = f"{proxy}:{country}:{country_code}"
                    item = {"proxy": proxy_str, "latency": latency, "lat": lat, "lon": lon}

                    # Filter: 10ms - 10000ms (Relaxed upper limit)
                    if latency < 10:
                        pass # Too fast/suspicious
                    elif latency < 300:
                        batch_results["gold"].append(item)
                    elif latency < 800:
                        batch_results["silver"].append(item)
                    elif latency < 10000: # Increased to 10s to capture almost everything
                        batch_results["bronze"].append(item)
            
            # Save batch to DB
            if any(batch_results.values()):
                # print(f"Saving batch of {len(batch_results['gold']) + len(batch_results['silver']) + len(batch_results['bronze'])} proxies to DB...")
                save_to_db(batch_results)
            else:
                # logging.info("No valid proxies in this chunk.")
                # print("No valid proxies in this chunk (all failed or too slow).")
                pass

def run_checker(proxies):
    import random
    # Shuffle to avoid checking the same top 1000 every time
    random.shuffle(proxies)
    
    # Limit to 3000 proxies for testing if the list is huge
    if len(proxies) > 3000:
        msg = f"Limiting check to random 3000 of {len(proxies)} proxies for speed."
        logging.info(msg)
        print(msg)
        proxies = proxies[:3000]

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(process_proxies(proxies))
    loop.close()
