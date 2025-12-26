from apscheduler.schedulers.blocking import BlockingScheduler
from sources import get_proxies
from checker import run_checker
import time
import logging
import os
import sys
from datetime import datetime

# Setup logging
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(BASE_DIR, "worker.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Add parent dir to path to import backend
sys.path.append(BASE_DIR)

def job():
    logging.info("Starting proxy check job...")
    print("Starting proxy check job...")
    try:
        # 1. Fetch
        print("Fetching proxies from sources...")
        proxies = get_proxies()
        logging.info(f"Fetched {len(proxies)} proxies.")
        print(f"Fetched {len(proxies)} proxies.")
        
        if not proxies:
            print("⚠️ No proxies fetched! Check network connection or sources.")
        
        # 2. Check & Save to DB
        run_checker(proxies)
        
        # 3. Save History Snapshot
        try:
            from backend.database import redis_client as db_client
            stats = db_client.get_stats()
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            db_client.save_history(
                timestamp, 
                stats.get("gold", 0), 
                stats.get("silver", 0), 
                stats.get("bronze", 0)
            )
            logging.info(f"History saved: {stats}")
            print(f"History saved: {stats}")
        except Exception as e:
            logging.error(f"Failed to save history: {e}")
            print(f"Failed to save history: {e}")

        logging.info("Job finished.")
        print("Job finished.")
    except Exception as e:
        logging.error(f"Job failed: {e}")
        print(f"Job failed: {e}")

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    # Run every 2 minutes
    scheduler.add_job(job, 'interval', minutes=2)
    
    print("Worker started. Press Ctrl+C to exit.")
    
    # Run once immediately on startup
    print("Running initial job...")
    job()
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
