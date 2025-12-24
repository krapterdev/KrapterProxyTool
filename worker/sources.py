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
    
    try:
        # Example: Fetch from a free proxy list (text format)
        # This is just an example source.
        response = requests.get("https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all")
        if response.status_code == 200:
            lines = response.text.splitlines()
            proxies.extend([line.strip() for line in lines if line.strip()])
            
        # Source 2: Geonode (Free List)
        try:
            response2 = requests.get("https://proxylist.geonode.com/api/proxy-list?limit=200&page=1&sort_by=lastChecked&sort_type=desc&protocols=http%2Chttps")
            if response2.status_code == 200:
                data = response2.json()
                for item in data.get('data', []):
                    proxies.append(f"{item['ip']}:{item['port']}")
        except:
            pass

        # Source 3: ProxyScrape (HTTP)
        try:
            r3 = requests.get("https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all")
            if r3.status_code == 200:
                proxies.extend([x.strip() for x in r3.text.splitlines() if x.strip()])
        except:
            pass

        # Source 4: Raw List (GitHub)
        try:
            r4 = requests.get("https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt")
            if r4.status_code == 200:
                proxies.extend([x.strip() for x in r4.text.splitlines() if x.strip()])
        except:
            pass
    except Exception as e:
        print(f"Error fetching proxies: {e}")
        
    return list(set(proxies)) # Deduplicate
