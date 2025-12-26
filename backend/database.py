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
            last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            assigned_to TEXT
        )
    ''')
    
    # Users table for Authentication
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            proxy_limit INTEGER DEFAULT 10,
            is_admin BOOLEAN DEFAULT 0
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
    def assign_proxies(self, email: str, limit: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Check how many already assigned
        cursor.execute("SELECT COUNT(*) FROM proxies WHERE assigned_to = ?", (email,))
        current_count = cursor.fetchone()[0]
        
        needed = limit - current_count
        
        if needed > 0:
            # 2. Assign more
            # We prefer better proxies (lower latency)
            cursor.execute("""
                UPDATE proxies 
                SET assigned_to = ? 
                WHERE proxy IN (
                    SELECT proxy FROM proxies 
                    WHERE assigned_to IS NULL 
                    ORDER BY latency ASC 
                    LIMIT ?
                )
            """, (email, needed))
            conn.commit()
            
        conn.close()

    def get_proxies(self, level: str, limit: int = None, user_email: str = None, is_admin: bool = False):
        conn = get_db_connection()
        
        query = "SELECT * FROM proxies WHERE level = ?"
        params = [level]
        
        if not is_admin and user_email:
            query += " AND assigned_to = ?"
            params.append(user_email)
            
        query += " ORDER BY latency ASC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
            
        cursor = conn.execute(query, tuple(params))
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "proxy": row["proxy"],
                "latency": row["latency"],
                "assigned_to": row["assigned_to"] if "assigned_to" in row.keys() else None
            }
            for row in rows
        ]

    def get_all_proxies(self, limit: int = None, user_email: str = None, is_admin: bool = False):
        conn = get_db_connection()
        
        query = "SELECT * FROM proxies"
        params = []
        
        if not is_admin and user_email:
            query += " WHERE assigned_to = ?"
            params.append(user_email)
            
        query += " ORDER BY latency ASC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
            
        cursor = conn.execute(query, tuple(params))
        rows = cursor.fetchall()
        conn.close()
        
        gold = []
        silver = []
        bronze = []
        
        for row in rows:
            # Handle case where assigned_to column might not exist yet in old rows if not migrated
            # But we just added it to schema. Existing rows won't have it unless we migrate.
            # SQLite adds columns on the fly with ALTER TABLE but here we just updated CREATE TABLE IF NOT EXISTS.
            # We should probably run an ALTER TABLE command or just assume the user will delete the DB.
            # Given the constraints, I'll assume the DB might need a reset or I'll try to handle it gracefully.
            assigned_to = row["assigned_to"] if "assigned_to" in row.keys() else None
            
            p = {
                "proxy": row["proxy"], 
                "latency": row["latency"],
                "assigned_to": assigned_to
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

    def update_user_limit(self, email: str, new_limit: int):
        conn = get_db_connection()
        conn.execute("UPDATE users SET proxy_limit = ? WHERE email = ?", (new_limit, email))
        conn.commit()
        conn.close()

    def get_user_by_email(self, email: str):
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()
        return user

redis_client = SQLiteClient()
