# proxy_config.py - Proxy Configuration for Yoga & Shopsy
# Format: host:port:user:pass

import os
import random
import threading

class ProxyManager:
    """Proxy manager for Yoga and Shopsy services"""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._yoga_index = 0
        
        # Your proxy credentials
        self.host = "dc.decodo.com"
        self.user = "sptu9f11ur"
        self.passwd = "0c_nm5z3eVm4jJEddL"
        
        # Proxy ports
        self.yoga_ports = list(range(10001, 10011))  # 10001-10010
        self.shopsy_ports = [10013, 10014]  # 10013-10014
        self.flipkart_ports = [10011, 10012]  # 10011-10012
        
    def get_proxy_url(self, port):
        """Convert to proxy URL format"""
        return f"http://{self.user}:{self.passwd}@{self.host}:{port}"
    
    def get_proxy_dict(self, port):
        """Get proxy dict for requests"""
        return {
            "http": self.get_proxy_url(port),
            "https": self.get_proxy_url(port)
        }
    
    # ==================== YOGA PROXIES ====================
    def get_yoga_proxies(self):
        """Get all Yoga proxies"""
        proxies = []
        for port in self.yoga_ports:
            proxies.append({
                "host": self.host,
                "port": port,
                "user": self.user,
                "pass": self.passwd,
                "url": self.get_proxy_url(port)
            })
        return proxies
    
    def get_yoga_proxy(self):
        """Get next Yoga proxy (round-robin)"""
        with self._lock:
            port = self.yoga_ports[self._yoga_index]
            self._yoga_index = (self._yoga_index + 1) % len(self.yoga_ports)
            return self.get_proxy_dict(port)
    
    def get_yoga_proxy_url(self):
        """Get next Yoga proxy URL string"""
        with self._lock:
            port = self.yoga_ports[self._yoga_index]
            self._yoga_index = (self._yoga_index + 1) % len(self.yoga_ports)
            return self.get_proxy_url(port)
    
    # ==================== SHOPSY PROXIES ====================
    def get_shopsy_proxies(self):
        """Get all Shopsy proxies"""
        proxies = []
        for port in self.shopsy_ports:
            proxies.append({
                "host": self.host,
                "port": port,
                "user": self.user,
                "pass": self.passwd,
                "url": self.get_proxy_url(port)
            })
        return proxies
    
    def get_shopsy_proxy(self):
        """Get random Shopsy proxy"""
        port = random.choice(self.shopsy_ports)
        return self.get_proxy_dict(port)
    
    def get_shopsy_proxy_url(self):
        """Get random Shopsy proxy URL string"""
        port = random.choice(self.shopsy_ports)
        return self.get_proxy_url(port)
    
    # ==================== FLIPKART PROXIES ====================
    def get_flipkart_proxies(self):
        """Get all Flipkart proxies"""
        proxies = []
        for port in self.flipkart_ports:
            proxies.append({
                "host": self.host,
                "port": port,
                "user": self.user,
                "pass": self.passwd,
                "url": self.get_proxy_url(port)
            })
        return proxies
    
    def get_flipkart_proxy(self):
        """Get random Flipkart proxy"""
        port = random.choice(self.flipkart_ports)
        return self.get_proxy_dict(port)
    
    def get_flipkart_proxy_url(self):
        """Get random Flipkart proxy URL string"""
        port = random.choice(self.flipkart_ports)
        return self.get_proxy_url(port)
    
    # ==================== GENERIC REQUEST WITH PROXY ====================
    def request_with_proxy(self, method, url, data=None, headers=None, proxy_type="yoga", timeout=30):
        """Make request with proxy rotation"""
        import requests
        
        proxy_dict = None
        if proxy_type == "yoga":
            proxy_dict = self.get_yoga_proxy()
        elif proxy_type == "shopsy":
            proxy_dict = self.get_shopsy_proxy()
        elif proxy_type == "flipkart":
            proxy_dict = self.get_flipkart_proxy()
        
        try:
            if method.upper() == "POST":
                return requests.post(url, json=data, headers=headers, timeout=timeout, proxies=proxy_dict)
            else:
                return requests.get(url, headers=headers, timeout=timeout, proxies=proxy_dict)
        except Exception as e:
            print(f"[Proxy] Request failed: {e}")
            return None

# Singleton instance
proxy_manager = ProxyManager()

# ==================== PROXY FUNCTIONS FOR MAIN.PY ====================
def get_yoga_proxy_url():
    """Get Yoga proxy URL for requests"""
    return proxy_manager.get_yoga_proxy_url()

def get_shopsy_proxy_url():
    """Get Shopsy proxy URL for requests"""
    return proxy_manager.get_shopsy_proxy_url()

def get_flipkart_proxy_url():
    """Get Flipkart proxy URL for requests"""
    return proxy_manager.get_flipkart_proxy_url()

def get_proxy_dict(proxy_type="yoga"):
    """Get proxy dict for requests"""
    if proxy_type == "yoga":
        return proxy_manager.get_yoga_proxy()
    elif proxy_type == "shopsy":
        return proxy_manager.get_shopsy_proxy()
    elif proxy_type == "flipkart":
        return proxy_manager.get_flipkart_proxy()
    return None

# Print proxy status
def print_proxy_status():
    """Print all proxy configurations"""
    print("\n" + "="*50)
    print("PROXY CONFIGURATION")
    print("="*50)
    print(f"\n🔹 Yoga Proxies ({len(proxy_manager.yoga_ports)}):")
    for port in proxy_manager.yoga_ports:
        print(f"   http://{proxy_manager.user}:****@{proxy_manager.host}:{port}")
    
    print(f"\n🔹 Shopsy Proxies ({len(proxy_manager.shopsy_ports)}):")
    for port in proxy_manager.shopsy_ports:
        print(f"   http://{proxy_manager.user}:****@{proxy_manager.host}:{port}")
    
    print(f"\n🔹 Flipkart Proxies ({len(proxy_manager.flipkart_ports)}):")
    for port in proxy_manager.flipkart_ports:
        print(f"   http://{proxy_manager.user}:****@{proxy_manager.host}:{port}")
    print("="*50 + "\n")

if __name__ == "__main__":
    print_proxy_status()
