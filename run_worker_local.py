import sys
import os
import asyncio
import logging

# Add 'worker' and 'backend' to path
sys.path.append(os.path.join(os.getcwd(), 'worker'))
sys.path.append(os.getcwd())

# Mock DB URL for local run if needed, or use the one from docker-compose if running on host with exposed ports
# Assuming Postgres is running on localhost:2224 (mapped from 5432)
os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:2224/proxies"

from worker.sources import get_proxies
from worker.checker import run_checker

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    print("--- Starting Local Worker Debug Run ---")
    
    # 1. Fetch
    print("Fetching proxies...")
    proxies = get_proxies()
    print(f"Fetched {len(proxies)} proxies from sources.")
    
    if not proxies:
        print("ERROR: No proxies fetched. Check internet connection or source URLs.")
        return

    # 2. Check & Save
    print("Running checker (this may take a while)...")
    try:
        run_checker(proxies)
        print("Checker finished.")
    except Exception as e:
        print(f"Checker failed: {e}")

if __name__ == "__main__":
    main()
