# supercoin.py - Shopsy Supercoin Fetcher Module
# NRTECNO SYSTEM

import asyncio
import time
import uuid
import json
import random
from curl_cffi import requests as cffi_requests

class ShopsySession:
    """NRTECNO Optimized Shopsy Session Handler"""
    
    def __init__(self):
        self.session = cffi_requests.Session(impersonate="chrome120")
        self.device_id = uuid.uuid4().hex[:32]
        self.visit_id = f"{uuid.uuid4().hex[:32]}-{int(time.time() * 1000)}"
        self.app_session = f"{uuid.uuid4()}_{int(time.time()*1000)}"
        self.current_dc = "1"
        self.tokens = {}
        self.user_id = None
        
    def _build_headers(self, is_game=False, extra_headers=None):
        """Generate complete headers for Shopsy API"""
        
        base_headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Content-Type": "application/json; charset=UTF-8",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "FK-TENANT-ID": "SHOPSY",
            "X-PARTNER-CONTEXT": json.dumps({"source": "reseller"}),
            "X-User-Agent": f"Mozilla/5.0 (Linux; Android 13; SM-S918B Build/TP1A.220624.014) FKUA/Retail/2291170/Android/Mobile (Samsung/SM-S918B/{self.device_id})",
            "X-Visit-Id": self.visit_id,
            "X-AppSession-ID": self.app_session,
            "X-Device-Id": self.device_id,
            "X-Platform": "android",
            "X-App-Version": "2291170",
            "city": "Delhi"
        }
        
        if is_game:
            base_headers.pop("X-Visit-Id", None)
            base_headers.pop("X-AppSession-ID", None)
            base_headers["sessionid"] = self.tokens.get("session_id", str(uuid.uuid4()))
            
        # Add auth tokens if available
        for token_key in ["at", "sn", "secureToken", "rt"]:
            if self.tokens.get(token_key):
                base_headers[token_key] = self.tokens[token_key]
                
        if extra_headers:
            base_headers.update(extra_headers)
            
        return base_headers
    
    async def request(self, method, path, data=None, is_game=False, retries=3):
        """Execute API request with automatic retry and DC failover"""
        
        url = f"https://{self.current_dc}.rome.api.flipkart.net{path}"
        headers = self._build_headers(is_game)
        
        for attempt in range(retries):
            try:
                if method.upper() == "POST":
                    resp = self.session.post(url, json=data, headers=headers, timeout=30)
                else:
                    resp = self.session.get(url, headers=headers, timeout=30)
                
                # Parse response
                try:
                    resp_json = resp.json()
                except:
                    resp_json = {}
                
                # Handle DC change
                if resp.status_code == 406 and resp_json.get("ERROR_MESSAGE") == "DC Change":
                    new_dc = resp_json.get("RESPONSE", {}).get("id") or resp_json.get("RESPONSE", {}).get("dc")
                    if new_dc:
                        self.current_dc = str(new_dc)
                        url = f"https://{self.current_dc}.rome.api.flipkart.net{path}"
                        continue
                
                # Extract session tokens from response
                self._extract_tokens(resp_json, resp.headers)
                
                return resp.status_code, resp_json
                
            except Exception as e:
                if attempt == retries - 1:
                    raise Exception(f"Request failed after {retries} attempts: {str(e)}")
                await asyncio.sleep(2 ** attempt)
                
        return 500, {"error": "Max retries exceeded"}
    
    def _extract_tokens(self, resp_json, resp_headers):
        """Extract and store session tokens from response"""
        
        # From response body
        if isinstance(resp_json, dict):
            session_block = resp_json.get("SESSION") or resp_json.get("RESPONSE", {}).get("SESSION") or {}
            
            for key in ["accountId", "at", "rt", "sn", "secureToken", "nsid", "vid", "email", "firstName", "lastName"]:
                if session_block.get(key):
                    self.tokens[key] = session_block[key]
                    
            if session_block.get("userId"):
                self.user_id = session_block["userId"]
                
            if session_block.get("isLoggedIn") is True:
                self.tokens["isLoggedIn"] = True
                
        # From headers
        headers_lower = {k.lower(): v for k, v in resp_headers.items()}
        for key in ["at", "rt", "sn", "nsid", "vid", "sessionid"]:
            if headers_lower.get(key):
                self.tokens[key] = headers_lower[key]
                
        return self.tokens

    async def request_otp(self, phone):
        """Step 1: Request OTP"""
        
        payload = {
            "actionRequestContext": {
                "type": "LOGIN_IDENTITY_VERIFY_SHOPSY2",
                "loginId": phone,
                "loginIdPrefix": "+91",
                "phoneNumberFormat": "E164",
                "addAppHash": True,
                "loginType": "MOBILE",
                "verificationType": "OTP",
                "sourceContext": "DEFAULT",
                "clientQueryParamMap": {
                    "version": "2",
                    "appName": "shopsy",
                    "client": "android"
                }
            }
        }
        
        status, response = await self.request("POST", "/1/action/view", payload)
        
        if status == 200:
            req_id = response.get("RESPONSE", {}).get("actionResponseContext", {}).get("requestId")
            if req_id:
                self.tokens["otpRequestId"] = req_id
                return True, req_id
                
        return False, response.get("error", "OTP request failed")
    
    async def verify_otp(self, phone, otp):
        """Step 2: Verify OTP and complete login"""
        
        payload = {
            "actionRequestContext": {
                "type": "LOGIN_SHOPSY2",
                "loginId": phone,
                "loginIdPrefix": "+91",
                "otp": otp,
                "otpRequestId": self.tokens.get("otpRequestId"),
                "remainingAttempts": 5,
                "phoneNumberFormat": "E164",
                "loginType": "MOBILE",
                "verificationType": "OTP",
                "sourceContext": "DEFAULT",
                "clientQueryParamMap": {
                    "version": "2",
                    "appName": "shopsy",
                    "client": "android"
                }
            }
        }
        
        status, response = await self.request("POST", "/1/action/view", payload)
        
        if status == 200:
            success = response.get("RESPONSE", {}).get("actionResponseContext", {}).get("authenticationSuccess", False)
            if success:
                self._extract_tokens(response, {})
                self.tokens["isLoggedIn"] = True
                return True, response
                
        return False, response.get("error", "OTP verification failed")
    
    async def load_user_state(self):
        """Step 3: Load user state"""
        
        payload = {
            "location": {"pincode": None},
            "ad": {
                "adId": str(uuid.uuid4()),
                "doNotPersonalizeAds": False,
                "sdkAdId": "",
                "adSdkVersion": "2.12.0"
            },
            "locale": {"deviceLanguage": "en", "shouldRefreshLanguage": False},
            "versions": {
                "cart": 1167987101,
                "userAccountState": 0,
                "abResponse": -2054295432,
                "abVariables": 0,
                "accountDetails": 1220048498,
                "wishlist": 0,
                "notifications": 861101,
                "location": 23273,
                "lockinResponse": 426889274
            }
        }
        
        status, response = await self.request("POST", "/4/user/state", payload)
        return status == 200
    
    async def fetch_coins(self):
        """Step 4: Fetch super coins"""
        
        if not self.user_id:
            self.user_id = self.tokens.get("accountId", "")
            
        payload = {
            "requestMethod": "GET",
            "routeUri": "user/get-user",
            "payload": {
                "userId": self.user_id,
                "userName": self.tokens.get("firstName", "User")
            }
        }
        
        status, response = await self.request("POST", "/1/shopsy/games", payload, is_game=True)
        
        if status == 200 and response.get("success"):
            data = response.get("data", {})
            earnings = data.get("earnings", {})
            coins = earnings.get("coinsEarnedTotal", 0)
            return {
                "total_coins": coins,
                "daily_coins": earnings.get("coinsEarnedDaily", 0),
                "weekly_coins": earnings.get("coinsEarnedWeekly", 0),
                "name": data.get("name", "N/A"),
                "user_id": data.get("userId", ""),
                "total_orders": data.get("totalOrders", 0),
                "data": data
            }
            
        return None

async def fetch_supercoins(phone, otp, progress_callback=None):
    """Main function to fetch supercoins"""
    
    client = ShopsySession()
    
    # Step 1: Request OTP
    if progress_callback:
        await progress_callback("📱 Requesting OTP...")
    
    success, req_id = await client.request_otp(phone)
    
    if not success:
        return {"status": "error", "message": f"OTP request failed: {req_id}"}
    
    # Step 2: Verify OTP
    if progress_callback:
        await progress_callback("🔐 Verifying OTP...")
    
    success, response = await client.verify_otp(phone, otp)
    
    if not success:
        return {"status": "error", "message": f"Login failed: {response}"}
    
    # Step 3: Load user state
    if progress_callback:
        await progress_callback("🔄 Loading profile...")
    
    await client.load_user_state()
    
    # Step 4: Fetch coins
    if progress_callback:
        await progress_callback("💰 Fetching coins...")
    
    result = await client.fetch_coins()
    
    if result:
        result["status"] = "success"
        result["phone"] = phone
        return result
    else:
        return {"status": "error", "message": "Failed to fetch coins"}
