import sqlite3
import os

DB_FILE = "proxies.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS proxies (
            proxy TEXT PRIMARY KEY,
            ip TEXT,
            port TEXT,
            country TEXT,
            country_code TEXT,
            latency INTEGER,
            level TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        
        # Format to match expected output
        return [
            {
                "proxy": row["proxy"], # "IP:PORT:COUNTRY:CODE" or just "IP:PORT"? Let's store full string in 'proxy' col for compatibility or reconstruct it.
                # Actually, let's store the full "IP:PORT:COUNTRY:CODE" string in the 'proxy' column to match previous behavior, 
                # OR reconstruct it. The frontend expects "proxy" key to have the full string.
                # Let's ensure the worker saves it as "IP:PORT:COUNTRY:CODE".
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

redis_client = SQLiteClient()
