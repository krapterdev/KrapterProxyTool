import os
import redis

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

class RedisClient:
    def __init__(self):
        self.client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

    def get_proxies(self, level: str):
        # Fetch all proxies from the sorted set (0 to -1 means all)
        proxies = self.client.zrange(f"proxies:{level}", 0, -1, withscores=True)
        return [{"proxy": p, "latency": int(s)} for p, s in proxies]

    def get_all_proxies(self):
        return {
            "gold": self.get_proxies("gold"),
            "silver": self.get_proxies("silver"),
            "bronze": self.get_proxies("bronze")
        }

    def get_stats(self):
        return {
            "gold": self.client.zcard("proxies:gold"),
            "silver": self.client.zcard("proxies:silver"),
            "bronze": self.client.zcard("proxies:bronze"),
        }

redis_client = RedisClient()
