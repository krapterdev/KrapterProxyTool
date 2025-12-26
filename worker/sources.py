import requests

def get_proxies():
    """
    Fetches proxies from external sources.
    Returns a list of proxies (ip:port).
    """
    # For demonstration, we'll use a hardcoded list and a public API if available.
    # In a real scenario, you'd add more sources here.
    
    proxies = [
        "1.1.1.1:80", # Dummy
        "8.8.8.8:80", # Dummy
    ]
    
    print("DEBUG: Starting proxy fetch...")
    
    try:
        # Example: Fetch from a free proxy list (text format)
        print("DEBUG: Fetching from ProxyScrape (Source 1)...")
        try:
            response = requests.get("https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all", timeout=10)
            if response.status_code == 200:
                lines = response.text.splitlines()
                count = len([line for line in lines if line.strip()])
                print(f"DEBUG: ProxyScrape (Source 1) returned {count} proxies.")
                proxies.extend([line.strip() for line in lines if line.strip()])
            else:
                print(f"DEBUG: ProxyScrape (Source 1) failed with status {response.status_code}")
        except Exception as e:
            print(f"DEBUG: ProxyScrape (Source 1) error: {e}")
            
        # Source 2: Geonode (Free List)
        print("DEBUG: Fetching from Geonode (Source 2)...")
        try:
            response2 = requests.get("https://proxylist.geonode.com/api/proxy-list?limit=200&page=1&sort_by=lastChecked&sort_type=desc&protocols=http%2Chttps", timeout=10)
            if response2.status_code == 200:
                data = response2.json()
                items = data.get('data', [])
                print(f"DEBUG: Geonode (Source 2) returned {len(items)} proxies.")
                for item in items:
                    proxies.append(f"{item['ip']}:{item['port']}")
            else:
                print(f"DEBUG: Geonode (Source 2) failed with status {response2.status_code}")
        except Exception as e:
            print(f"DEBUG: Geonode (Source 2) error: {e}")

        # Source 3: ProxyScrape (HTTP) - Redundant but kept for safety
        print("DEBUG: Fetching from ProxyScrape (Source 3)...")
        try:
            r3 = requests.get("https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all", timeout=10)
            if r3.status_code == 200:
                lines = r3.text.splitlines()
                count = len([x for x in lines if x.strip()])
                print(f"DEBUG: ProxyScrape (Source 3) returned {count} proxies.")
                proxies.extend([x.strip() for x in lines if x.strip()])
            else:
                print(f"DEBUG: ProxyScrape (Source 3) failed with status {r3.status_code}")
        except Exception as e:
            print(f"DEBUG: ProxyScrape (Source 3) error: {e}")

        # Source 4: Raw List (GitHub)
        print("DEBUG: Fetching from GitHub TheSpeedX (Source 4)...")
        try:
            r4 = requests.get("https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt", timeout=10)
            if r4.status_code == 200:
                lines = r4.text.splitlines()
                count = len([x for x in lines if x.strip()])
                print(f"DEBUG: GitHub TheSpeedX (Source 4) returned {count} proxies.")
                proxies.extend([x.strip() for x in lines if x.strip()])
            else:
                print(f"DEBUG: GitHub TheSpeedX (Source 4) failed with status {r4.status_code}")
        except Exception as e:
            print(f"DEBUG: GitHub TheSpeedX (Source 4) error: {e}")

    except Exception as e:
        print(f"Error fetching proxies: {e}")
        
    unique_proxies = list(set(proxies))
    print(f"DEBUG: Total unique proxies fetched: {len(unique_proxies)}")
    return unique_proxies
