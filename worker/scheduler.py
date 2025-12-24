from apscheduler.schedulers.blocking import BlockingScheduler
from sources import get_proxies
from checker import run_checker
import time

def job():
    print("Starting proxy check job...")
    proxies = get_proxies()
    print(f"Fetched {len(proxies)} proxies.")
    run_checker(proxies)
    print("Job finished.")

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
