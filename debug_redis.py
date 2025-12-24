import redis
import os

# Configuration matching start.py and docker-compose
REDIS_HOST = "localhost"
REDIS_PORT = 6380
REDIS_DB = 0

def check_redis():
    print(f"Connecting to Redis at {REDIS_HOST}:{REDIS_PORT}...")
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
        
        # Ping
        if r.ping():
            print("✅ Redis connection successful!")
        
        # Check Keys
        keys = r.keys("*")
        print(f"🔑 Found {len(keys)} keys: {keys}")
        
        # Check specific key
        level1_proxies = r.zrange("proxies:level1", 0, -1, withscores=True)
        print(f"📊 proxies:level1 content: {level1_proxies}")
        
        if not level1_proxies:
            print("❌ 'proxies:level1' is EMPTY or MISSING.")
        else:
            print("✅ 'proxies:level1' has data.")

    except Exception as e:
        print(f"❌ Error connecting to Redis: {e}")

if __name__ == "__main__":
    check_redis()
