import requests
import time

# ==============================================================================
# COPY THIS CLASS TO YOUR OTHER PROJECT
# ==============================================================================
class KrapterProxyClient:
    """
    Professional Python Client for KrapterProxyTool.
    Use this to integrate proxies into your bots, scrapers, or automation tools.
    """
    
    def __init__(self, base_url="http://localhost:2223", token=None, api_key=None):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({"X-API-Key": api_key})
        elif token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})
            
    def get_random_proxy(self, format="json"):
        """
        Fetches a single random high-quality proxy.
        Returns dict if format='json', or string 'ip:port' if format='text'.
        """
        try:
            resp = self.session.get(f"{self.base_url}/api/proxies/random", params={"format": format})
            resp.raise_for_status()
            if format == "text":
                return resp.text.strip()
            return resp.json()
        except Exception as e:
            print(f"[KrapterSDK] Error fetching proxy: {e}")
            return None

    def get_all_proxies(self, limit=None):
        """
        Fetches list of all available proxies.
        """
        try:
            params = {}
            if limit:
                params["limit"] = limit
            resp = self.session.get(f"{self.base_url}/api/proxies/external", params=params)
            resp.raise_for_status()
            return resp.text.splitlines()
        except Exception as e:
            print(f"[KrapterSDK] Error fetching list: {e}")
            return []

    def rotate(self, delay=0):
        """
        Generator that yields a fresh proxy indefinitely.
        Useful for loops.
        """
        while True:
            proxy = self.get_random_proxy(format="text")
            if proxy:
                yield proxy
            else:
                time.sleep(5) # Wait if no proxies
            
            if delay > 0:
                time.sleep(delay)

# ==============================================================================
# EXAMPLE USAGE
# ==============================================================================
if __name__ == "__main__":
    # 1. Get this from your Dashboard (http://localhost:2222)
    API_KEY = "sk_live_REPLACE_WITH_YOUR_KEY_HERE" 

    # 2. The URL where KrapterProxyTool backend is running
    BACKEND_URL = "http://localhost:2223" 

    print(f"Initializing Client with API Key: {API_KEY[:10]}...")
    
    # Initialize the client
    client = KrapterProxyClient(
        base_url=BACKEND_URL,
        api_key=API_KEY
    )

    # Example 1: Get a single random proxy
    print("\n--- 1. Fetching Random Proxy ---")
    proxy = client.get_random_proxy()
    if proxy:
        print(f"Success! Proxy: {proxy}")
    else:
        print("Failed to fetch proxy. Check your API Key or Backend URL.")

    # Example 2: Get a list of proxies
    print("\n--- 2. Fetching Proxy List (Limit 3) ---")
    proxies = client.get_all_proxies(limit=3)
    for p in proxies:
        print(f" - {p}")

    # Example 3: Using in a loop (Rotation)
    print("\n--- 3. Simulating Rotation (Fetching 3 times) ---")
    count = 0
    for proxy in client.rotate(delay=1):
        print(f"Request {count+1} using: {proxy}")
        count += 1
        if count >= 3:
            break
