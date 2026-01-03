import asyncio
import os
import random
import time
from backend.database import Database
from backend.auth import get_password_hash

# Mock Data
MOCK_PROXIES = [
    "1.1.1.1:80:US:US",
    "8.8.8.8:53:US:US",
    "104.21.55.2:80:CA:CA",
    "185.228.168.9:80:DE:DE",
    "45.90.28.0:80:NL:NL",
    "103.152.18.18:80:SG:SG",
    "203.0.113.1:8080:JP:JP",
    "198.51.100.1:3128:GB:GB",
    "192.0.2.1:80:FR:FR",
    "100.64.0.1:80:AU:AU",
    "172.16.0.1:80:BR:BR",
    "10.0.0.1:80:IN:IN",
]

async def seed():
    print("🌱 Seeding Database...")
    db = Database()
    await db.connect()
    
    # 1. Initialize Tables
    print("   - Initializing tables...")
    await db.init_db()
    
    # 2. Create Admin User if not exists
    print("   - Checking Admin User...")
    user = await db.get_user_by_email("admin@proxyhub.io")
    if not user:
        print("   - Creating Admin User...")
        await db.create_user("admin@proxyhub.io", get_password_hash("admin123"), is_admin=True)
    else:
        print("   - Admin User exists.")

    # 3. Clear existing proxies (optional, but good for clean slate)
    # await db.pool.execute("DELETE FROM proxies")

    # 4. Insert Mock Proxies
    print("   - Inserting Mock Proxies...")
    for p_str in MOCK_PROXIES:
        parts = p_str.split(":")
        ip = parts[0]
        port = int(parts[1])
        country = parts[2]
        country_code = parts[3]
        
        # Randomize latency and level
        latency = random.randint(10, 5000)
        if latency < 300:
            level = "gold"
        elif latency < 1000:
            level = "silver"
        else:
            level = "bronze"
            
        # Randomize coordinates (approximate)
        lat = random.uniform(-90, 90)
        lon = random.uniform(-180, 180)
        
        await db.save_proxy(
            proxy=p_str,
            latency=latency,
            level=level,
            country=country,
            country_code=country_code,
            lat=lat,
            lon=lon
        )
        
    print("✅ Seeding Complete! Restart backend to see changes.")
    await db.close()

if __name__ == "__main__":
    # Ensure we are in the root directory
    if not os.path.exists("backend"):
        print("❌ Please run this script from the project root directory.")
        exit(1)
        
    asyncio.run(seed())
