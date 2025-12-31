import requests
import time

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
        Useful for loops:
            for proxy in client.rotate():
                requests.get(..., proxies={"http": proxy})
        """
        while True:
            proxy = self.get_random_proxy(format="text")
            if proxy:
                yield proxy
            else:
                time.sleep(5) # Wait if no proxies
            
            if delay > 0:
                time.sleep(delay)

# Example Usage
if __name__ == "__main__":
    # Replace with your API Key from the dashboard
    API_KEY = "sk_live_..." 
    client = KrapterProxyClient(api_key=API_KEY)
    
    print("--- Fetching Random Proxy ---")
    p = client.get_random_proxy()
    print(f"Got Proxy: {p}")
    
    print("\n--- Fetching List ---")
    all_p = client.get_all_proxies(limit=5)
    print(f"First 5 proxies: {all_p}")
