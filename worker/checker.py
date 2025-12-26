import asyncio
import aiohttp
import time
import sqlite3
import os
import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(BASE_DIR, "proxies.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS proxies (
            proxy TEXT PRIMARY KEY,
            ip TEXT,
            port TEXT,
            country TEXT,
            country_code TEXT,
            latency INTEGER,
            level TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            assigned_to TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Initialize DB
init_db()

def save_to_db(new_proxies):
    try:
        conn = sqlite3.connect(DB_FILE)
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
                cursor.execute('''
                    INSERT INTO proxies (proxy, ip, port, country, country_code, latency, level, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(proxy) DO UPDATE SET
                        latency=excluded.latency,
                        level=excluded.level,
                        last_updated=CURRENT_TIMESTAMP
                ''', (proxy_str, ip, port, country, country_code, latency, level))
                count += 1
                
        conn.commit()
        conn.close()
        logging.info(f"Saved {count} proxies to DB.")
    except Exception as e:
        logging.error(f"Error saving to DB: {e}")

async def check_proxy(session, proxy):
    # Use ip-api to get country and validate proxy
    url = "http://ip-api.com/json"
    proxy_url = f"http://{proxy}"
    start_time = time.time()
    
    try:
        async with session.get(url, proxy=proxy_url, timeout=10) as response:
            if response.status == 200:
                latency = int((time.time() - start_time) * 1000) # ms
                data = await response.json()
                country = data.get("country", "Unknown")
                country_code = data.get("countryCode", "UN")
                return proxy, latency, country, country_code
            else:
                pass
    except Exception as e:
        # logging.debug(f"Proxy check failed for {proxy}: {e}")
        pass
    return proxy, None, None, None

async def process_proxies(proxies):
    chunk_size = 50
    logging.info(f"Processing {len(proxies)} proxies...")
    
    for i in range(0, len(proxies), chunk_size):
        chunk = proxies[i:i + chunk_size]
        logging.info(f"Checking chunk {i}/{len(proxies)}...")
        
        async with aiohttp.ClientSession() as session:
            tasks = [check_proxy(session, proxy) for proxy in chunk]
            results = await asyncio.gather(*tasks)
            
            batch_results = {"gold": [], "silver": [], "bronze": []}

            for proxy, latency, country, country_code in results:
                if latency is not None:
                    proxy_str = f"{proxy}:{country}:{country_code}"
                    item = {"proxy": proxy_str, "latency": latency}

                    # Filter: 50ms - 1200ms
                    if latency < 50:
                        pass # Too fast/suspicious
                    elif latency < 300:
                        batch_results["gold"].append(item)
                    elif latency < 800:
                        batch_results["silver"].append(item)
                    elif latency < 1200:
                        batch_results["bronze"].append(item)
            
            # Save batch to DB
            if any(batch_results.values()):
                save_to_db(batch_results)
            else:
                logging.info("No valid proxies in this chunk.")

def run_checker(proxies):
    # Limit to 1000 proxies for testing if the list is huge
    if len(proxies) > 1000:
        logging.info(f"Limiting check to first 1000 of {len(proxies)} proxies for speed.")
        proxies = proxies[:1000]

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(process_proxies(proxies))
    loop.close()
