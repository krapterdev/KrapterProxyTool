from apscheduler.schedulers.blocking import BlockingScheduler
from sources import get_proxies
from checker import run_checker
import time

import logging
import os

# Setup logging
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(BASE_DIR, "worker.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def job():
    logging.info("Starting proxy check job...")
    print("Starting proxy check job...")
    try:
        proxies = get_proxies()
        logging.info(f"Fetched {len(proxies)} proxies.")
        print(f"Fetched {len(proxies)} proxies.")
        run_checker(proxies)
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
    # Run once immediately on startup
    print("Running initial job...")
    job()
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
