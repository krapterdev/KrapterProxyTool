import psycopg2
from psycopg2.extras import RealDictCursor
import os
import redis
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Env vars
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/proxies")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

def get_db_connection():
    conn = psycopg2.connect(DB_URL)
    return conn

def init_db():
    # Wait for DB to be ready
    retries = 5
    while retries > 0:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Proxies table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS proxies (
                    proxy TEXT PRIMARY KEY,
                    ip TEXT,
                    port TEXT,
                    latency INTEGER,
                    country TEXT,
                    country_code TEXT,
                    level TEXT,
                    last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    assigned_to TEXT
                )
            ''')
            
            # Migration: Add columns if they don't exist (for existing DBs)
            try:
                cursor.execute("ALTER TABLE proxies ADD COLUMN IF NOT EXISTS ip TEXT")
                cursor.execute("ALTER TABLE proxies ADD COLUMN IF NOT EXISTS port TEXT")
                conn.commit()
            except Exception as e:
                print(f"Migration warning: {e}")
                conn.rollback()
            
            # Users table for Authentication
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    proxy_limit INTEGER DEFAULT 10,
                    is_admin BOOLEAN DEFAULT FALSE
                )
            ''')

            # History table for Graph
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS proxy_history (
                    id SERIAL PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    gold_count INTEGER DEFAULT 0,
                    silver_count INTEGER DEFAULT 0,
                    bronze_count INTEGER DEFAULT 0
                )
            ''')
            
            conn.commit()
            conn.close()
            print("Database initialized successfully.")
            break
        except Exception as e:
            print(f"DB not ready yet, retrying... ({e})")
            time.sleep(2)
            retries -= 1

# Initialize DB on import (or call explicitly in main)
init_db()

class PostgresClient:
    def assign_proxies(self, email: str, limit: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Check how many already assigned
        cursor.execute("SELECT COUNT(*) FROM proxies WHERE assigned_to = %s", (email,))
        current_count = cursor.fetchone()[0]
        
        needed = limit - current_count
        
        if needed > 0:
            # 2. Assign more
            # We prefer better proxies (lower latency)
            cursor.execute("""
                UPDATE proxies 
                SET assigned_to = %s 
                WHERE proxy IN (
                    SELECT proxy FROM proxies 
                    WHERE assigned_to IS NULL 
                    AND level != 'gold'
                    ORDER BY latency ASC 
                    LIMIT %s
                )
            """, (email, needed))
            conn.commit()
            
        conn.close()

    def get_proxies(self, level: str, limit: int = None, user_email: str = None, is_admin: bool = False):
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = "SELECT * FROM proxies WHERE level = %s"
        params = [level]
        
        if not is_admin and user_email:
            query += " AND assigned_to = %s"
            params.append(user_email)
            
        query += " ORDER BY latency ASC"
        
        if limit:
            query += " LIMIT %s"
            params.append(limit)
            
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]

    def get_all_proxies(self, limit: int = None, user_email: str = None, is_admin: bool = False):
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = "SELECT * FROM proxies"
        params = []
        
        if not is_admin and user_email:
            query += " WHERE assigned_to = %s"
            params.append(user_email)
            
        query += " ORDER BY latency ASC"
        
        if limit:
            query += " LIMIT %s"
            params.append(limit)
            
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        conn.close()
        
        gold = []
        silver = []
        bronze = []
        
        for row in rows:
            p = {
                "proxy": row["proxy"], 
                "latency": row["latency"],
                "assigned_to": row.get("assigned_to")
            }
            if row["level"] == "gold":
                gold.append(p)
            elif row["level"] == "silver":
                silver.append(p)
            elif row["level"] == "bronze":
                bronze.append(p)
                
        return {
            "gold": gold,
            "silver": silver,
            "bronze": bronze
        }

    def get_stats(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        stats = {}
        for level in ["gold", "silver", "bronze"]:
            cursor.execute("SELECT COUNT(*) FROM proxies WHERE level = %s", (level,))
            stats[level] = cursor.fetchone()[0]
        conn.close()
        return stats

    def get_all_rows(self):
        """Helper for Excel export"""
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM proxies ORDER BY latency ASC")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def save_history(self, timestamp, gold, silver, bronze):
        """Save a snapshot of proxy counts to history"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO proxy_history (timestamp, gold_count, silver_count, bronze_count) VALUES (%s, %s, %s, %s)",
            (timestamp, gold, silver, bronze)
        )
        conn.commit()
        conn.close()

    def get_history(self, limit=20):
        """Get recent history for the graph"""
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM proxy_history ORDER BY id DESC LIMIT %s", (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        # Return in reverse order (oldest first) for the graph
        return [dict(row) for row in reversed(rows)]

    def update_user_limit(self, email: str, new_limit: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET proxy_limit = %s WHERE email = %s", (new_limit, email))
        conn.commit()
        conn.close()

    def get_user_by_email(self, email: str):
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        conn.close()
        return user

# Use Redis for caching if needed later, currently just DB wrapper
redis_client = PostgresClient()
