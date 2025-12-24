import asyncio
import aiohttp
import time
import redis
import os

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

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
        pass
    return proxy, None, None, None

async def process_proxies(proxies):
    chunk_size = 50
    for i in range(0, len(proxies), chunk_size):
        chunk = proxies[i:i + chunk_size]
        # print(f"Checking chunk {i}/{len(proxies)}...")
        
        async with aiohttp.ClientSession() as session:
            tasks = [check_proxy(session, proxy) for proxy in chunk]
            results = await asyncio.gather(*tasks)
            
            for proxy, latency, country, country_code in results:
                if latency is not None:
                    # Filter: 50ms - 1200ms
                    if latency < 50:
                        pass # Too fast/suspicious
                    elif latency < 300:
                        level = "gold"
                        # Store as "IP:PORT:COUNTRY:CODE"
                        redis_client.zadd(f"proxies:{level}", {f"{proxy}:{country}:{country_code}": latency})
                    elif latency < 800:
                        level = "silver"
                        redis_client.zadd(f"proxies:{level}", {f"{proxy}:{country}:{country_code}": latency})
                    elif latency < 1200:
                        level = "bronze"
                        redis_client.zadd(f"proxies:{level}", {f"{proxy}:{country}:{country_code}": latency})
                    # Dropping > 1200ms

def run_checker(proxies):
    # Limit to 1000 proxies for testing if the list is huge
    if len(proxies) > 1000:
        # print(f"⚠️ Limiting check to first 1000 of {len(proxies)} proxies for speed.")
        proxies = proxies[:1000]

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(process_proxies(proxies))
    loop.close()
