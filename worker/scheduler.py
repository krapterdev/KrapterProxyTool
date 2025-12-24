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
    
    # Inject fake data for immediate feedback
    try:
        from checker import save_to_db
        print("Injecting initial data for UI verification...")
        fake_data = {
            "gold": [
                {"proxy": "104.28.205.166:80:US:US", "latency": 120},
                {"proxy": "185.199.110.153:443:DE:DE", "latency": 150},
                {"proxy": "45.79.19.196:8080:SG:SG", "latency": 200}
            ],
            "silver": [],
            "bronze": []
        }
        save_to_db(fake_data)
        print("Initial data injected.")
    except Exception as e:
        print(f"Failed to inject initial data: {e}")

    job()
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
