import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "proxies.db")

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Proxies table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS proxies (
            proxy TEXT PRIMARY KEY,
            latency INTEGER,
            country TEXT,
            country_code TEXT,
            level TEXT,
            last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Users table for Authentication
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')

    # History table for Graph
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS proxy_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            gold_count INTEGER DEFAULT 0,
            silver_count INTEGER DEFAULT 0,
            bronze_count INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize DB on import
init_db()

class SQLiteClient:
    def get_proxies(self, level: str):
        conn = get_db_connection()
        cursor = conn.execute("SELECT * FROM proxies WHERE level = ? ORDER BY latency ASC", (level,))
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "proxy": row["proxy"],
                "latency": row["latency"]
            }
            for row in rows
        ]

    def get_all_proxies(self):
        return {
            "gold": self.get_proxies("gold"),
            "silver": self.get_proxies("silver"),
            "bronze": self.get_proxies("bronze")
        }

    def get_stats(self):
        conn = get_db_connection()
        stats = {}
        for level in ["gold", "silver", "bronze"]:
            count = conn.execute("SELECT COUNT(*) FROM proxies WHERE level = ?", (level,)).fetchone()[0]
            stats[level] = count
        conn.close()
        return stats

    def get_all_rows(self):
        """Helper for Excel export"""
        conn = get_db_connection()
        cursor = conn.execute("SELECT * FROM proxies ORDER BY latency ASC")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def save_history(self, timestamp, gold, silver, bronze):
        """Save a snapshot of proxy counts to history"""
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO proxy_history (timestamp, gold_count, silver_count, bronze_count) VALUES (?, ?, ?, ?)",
            (timestamp, gold, silver, bronze)
        )
        conn.commit()
        conn.close()

    def get_history(self, limit=20):
        """Get recent history for the graph"""
        conn = get_db_connection()
        cursor = conn.execute("SELECT * FROM proxy_history ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        # Return in reverse order (oldest first) for the graph
        return [dict(row) for row in reversed(rows)]

redis_client = SQLiteClient()
