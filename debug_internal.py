import psycopg2
import os
from datetime import datetime

# DB Config for Internal Docker Network
DB_HOST = "db"
DB_PORT = "5432"
DB_NAME = "proxies"
DB_USER = "postgres"
DB_PASS = "postgres"

def check_db():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cur = conn.cursor()
        
        print("--- Database Connection Successful (Internal) ---")
        
        # Check Proxies Count
        cur.execute("SELECT COUNT(*) FROM proxies;")
        count = cur.fetchone()[0]
        print(f"Total Proxies: {count}")
        
        if count > 0:
            # Check Last Updated
            cur.execute("SELECT MAX(last_checked) FROM proxies;")
            last_checked = cur.fetchone()[0]
            print(f"Last Scrape Time: {last_checked}")
            
            # Check Levels
            cur.execute("SELECT level, COUNT(*) FROM proxies GROUP BY level;")
            levels = cur.fetchall()
            print("Proxy Levels:", levels)
        else:
            print("WARNING: No proxies found in the database!")

        # Check Users
        cur.execute("SELECT email, api_key FROM users;")
        users = cur.fetchall()
        print("\n--- Users ---")
        for u in users:
            print(f"Email: {u[0]}, API Key: {u[1]}")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    check_db()
