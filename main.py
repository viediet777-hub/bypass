#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# VIEDIET UTILITY BOT - ALL FEATURES WORKING WITH PROXY

import os
import logging
import telebot
import requests
import json
import time
import threading
import re
import random
import string
import instaloader
import shutil
import tempfile
import hashlib
import zipfile
import sqlite3
import asyncio
import urllib.parse
import base64
import uuid
from datetime import datetime, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from curl_cffi import requests as cffi_requests

# ==================== PROXY CONFIGURATION ====================
class ProxyManager:
    """Proxy manager for Yoga, Shopsy, and Flipkart services"""
    
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
    def get_shopsy_proxy(self):
        """Get random Shopsy proxy"""
        port = random.choice(self.shopsy_ports)
        return self.get_proxy_dict(port)
    
    def get_shopsy_proxy_url(self):
        """Get random Shopsy proxy URL string"""
        port = random.choice(self.shopsy_ports)
        return self.get_proxy_url(port)
    
    # ==================== FLIPKART PROXIES ====================
    def get_flipkart_proxy(self):
        """Get random Flipkart proxy"""
        port = random.choice(self.flipkart_ports)
        return self.get_proxy_dict(port)
    
    def get_flipkart_proxy_url(self):
        """Get random Flipkart proxy URL string"""
        port = random.choice(self.flipkart_ports)
        return self.get_proxy_url(port)

# Initialize proxy manager
proxy_manager = ProxyManager()

def get_yoga_proxy_url():
    return proxy_manager.get_yoga_proxy_url()

def get_shopsy_proxy_url():
    return proxy_manager.get_shopsy_proxy_url()

def get_flipkart_proxy_url():
    return proxy_manager.get_flipkart_proxy_url()

def get_proxy_dict(proxy_type="yoga"):
    if proxy_type == "yoga":
        return proxy_manager.get_yoga_proxy()
    elif proxy_type == "shopsy":
        return proxy_manager.get_shopsy_proxy()
    elif proxy_type == "flipkart":
        return proxy_manager.get_flipkart_proxy()
    return None

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False

from menu import (
    main_menu_text, main_menu_keyboard,
    firebase_menu_text, firebase_menu_keyboard,
    temp_menu_text, temp_menu_keyboard,
    flipkart_menu_text, flipkart_menu_keyboard,
    instagram_menu_text, instagram_menu_keyboard,
    igviewer_menu_text, igviewer_menu_keyboard,
    music_menu_text, music_menu_keyboard,
    shopsy_menu_text, shopsy_menu_keyboard,
    supercoin_menu_text, supercoin_menu_keyboard,
    yoga_menu_text, yoga_menu_keyboard,
    referral_menu_text, referral_menu_keyboard,
    admin_panel_text, admin_panel_keyboard,
    help_menu_text,
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("BOT_TOKEN environment variable not set.")
    exit(1)

ADMIN_ID = int(os.environ.get("ADMIN_ID", 1364476174))
CHANNEL_USERNAME = "viedietlooters"
REFERRAL_BONUS = 3
NEW_USER_BONUS = 5
REFERRAL_STAY_HOURS = 1
YOGA_REFER_REWARD = 4
YOGA_WELCOME_BONUS = 2

DEFAULT_COSTS = {
    "firebase": 2, "flipkart": 1, "instagram_single": 1, "instagram_bulk": 1,
    "shopsy": 1, "yoga": 1, "igviewer": 1, "supercoin": 1,
}

YOGA_REGISTER_URL = "https://auth-service.habuild.in/public/user/v1/register-user"
YOGA_LOGIN_URL = "https://auth-service.habuild.in/public/auth/v1/login"
YOGA_VERIFY_URL = "https://auth-service.habuild.in/public/auth/v1/verify-otp"

YOGA_HEADERS = {
    "accept": "application/json", "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json", "origin": "https://habit.yoga",
    "referer": "https://habit.yoga/", "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors", "sec-fetch-site": "cross-site",
    "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1",
}
YOGA_REG_HEADERS = {**YOGA_HEADERS, "authorization": "Bearer"}

YOGA_NAMES = [
    "Aarav","Vivaan","Aditya","Vihaan","Arjun","Sai","Shaurya","Atharva","Yash","Dhruv",
    "Kabir","Reyansh","Krishna","Laksh","Advik","Pranav","Rudra","Ishaan","Dev","Ansh",
    "Anaya","Aaradhya","Navya","Myra","Ananya","Diya","Sara","Ishita","Aadhya","Riya",
    "Raj","Simran","Priya","Rahul","Neha","Amit","Pooja","Vikram","Anjali","Rohan",
]

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

DB_PATH = "viediet_bot.db"
SHOPSY_SESSIONS_DIR = "shopsy_sessions"
os.makedirs(SHOPSY_SESSIONS_DIR, exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT,
        balance INTEGER DEFAULT 15, status TEXT DEFAULT 'ACTIVE',
        registered_at TEXT, last_used TEXT, referred_by INTEGER DEFAULT NULL,
        referral_code TEXT UNIQUE, account_age_days INTEGER DEFAULT 0,
        is_valid INTEGER DEFAULT 1, ip_address TEXT DEFAULT NULL,
        last_check TEXT DEFAULT NULL, shopsy_balance INTEGER DEFAULT 0,
        shopsy_is_logged_in INTEGER DEFAULT 0, yoga_code TEXT DEFAULT NULL,
        yoga_refers INTEGER DEFAULT 0, yoga_bot_refers INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS referrals (
        id INTEGER PRIMARY KEY AUTOINCREMENT, referrer_id INTEGER,
        referred_id INTEGER UNIQUE, join_timestamp TEXT,
        leave_timestamp TEXT DEFAULT NULL, points_awarded INTEGER DEFAULT 0,
        is_valid INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS pending_referrals (
        id INTEGER PRIMARY KEY AUTOINCREMENT, referrer_id INTEGER,
        referred_id INTEGER UNIQUE, join_timestamp TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS usage_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
        module TEXT, details TEXT, timestamp TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS shopsy_sessions (
        user_id INTEGER PRIMARY KEY, phone TEXT, session_data TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS shopsy_mining_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, phone TEXT,
        coins_earned INTEGER, games_played INTEGER, gems_earned INTEGER,
        time_taken INTEGER, mined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS temp_emails (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, email TEXT,
        password TEXT, token TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()
    logger.info("Database initialized.")

init_db()

def run_scheduled_tasks():
    while True:
        try:
            check_and_award_referrals()
        except Exception as e:
            logger.error(f"[SCHEDULED] Referral check error: {e}")
        try:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute("DELETE FROM temp_emails WHERE created_at <= datetime('now', '-10 minutes')")
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"[SCHEDULED] Temp email cleanup error: {e}")
        time.sleep(300)

task_thread = threading.Thread(target=run_scheduled_tasks, daemon=True)
task_thread.start()

class CreditManager:
    def __init__(self, user_id, cost, operation_name=""):
        self.user_id = user_id; self.cost = cost; self.operation_name = operation_name
        self.deducted = False; self.balance_before = 0
    def __enter__(self): return self
    def deduct(self):
        self.balance_before = get_user_balance(self.user_id)
        if self.balance_before < self.cost:
            raise ValueError(f"Insufficient credits! Need {self.cost}")
        update_user_balance(self.user_id, -self.cost)
        self.deducted = True; return self
    def refund(self):
        if self.deducted:
            update_user_balance(self.user_id, self.cost)
            self.deducted = False; return True
        return False
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None: self.refund(); return False

def get_user(user_id):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor(); c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    row = c.fetchone(); conn.close()
    if row:
        return {'user_id': row[0], 'username': row[1], 'first_name': row[2],
            'balance': row[3], 'status': row[4], 'registered_at': row[5],
            'last_used': row[6], 'referred_by': row[7], 'referral_code': row[8],
            'account_age_days': row[9], 'is_valid': row[10], 'ip_address': row[11],
            'last_check': row[12], 'shopsy_balance': row[13] if len(row) > 13 else 0,
            'shopsy_is_logged_in': row[14] if len(row) > 14 else 0,
            'yoga_code': row[15] if len(row) > 15 else None,
            'yoga_refers': row[16] if len(row) > 16 else 0,
            'yoga_bot_refers': row[17] if len(row) > 17 else 0}
    return None

def create_user(user_id, username, first_name, referred_by=None):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor(); now = datetime.now().isoformat()
    ref_code = f"REF{user_id}{random.randint(1000, 9999)}"
    c.execute('''INSERT OR IGNORE INTO users
        (user_id, username, first_name, balance, status, registered_at, last_used, referred_by, referral_code)
        VALUES (?, ?, ?, ?, 'ACTIVE', ?, ?, ?, ?)''',
        (user_id, username, first_name, NEW_USER_BONUS, now, now, referred_by, ref_code))
    conn.commit(); conn.close()
    if referred_by: add_pending_referral(referred_by, user_id)
    return NEW_USER_BONUS

def update_user_balance(user_id, delta):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (delta, user_id))
    conn.commit(); conn.close()

def get_user_balance(user_id):
    user = get_user(user_id); return user['balance'] if user else 15

def get_shopsy_balance(user_id):
    user = get_user(user_id); return user['shopsy_balance'] if user else 0

def update_shopsy_balance(user_id, amount):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('UPDATE users SET shopsy_balance = shopsy_balance + ? WHERE user_id = ?', (amount, user_id))
    conn.commit(); conn.close()

def get_shopsy_login_status(user_id):
    user = get_user(user_id); return user.get('shopsy_is_logged_in', 0) if user else 0

def set_shopsy_login_status(user_id, status):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('UPDATE users SET shopsy_is_logged_in = ? WHERE user_id = ?', (1 if status else 0, user_id))
    conn.commit(); conn.close()

def get_referral_count(user_id):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM referrals WHERE referrer_id = ? AND is_valid = 1', (user_id,))
    count = c.fetchone()[0]; conn.close(); return count

def get_pending_referral_count(user_id):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM pending_referrals WHERE referrer_id = ?', (user_id,))
    count = c.fetchone()[0]; conn.close(); return count

def add_pending_referral(referrer_id, referred_id):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor(); now = datetime.now().isoformat()
    try:
        c.execute('INSERT INTO pending_referrals (referrer_id, referred_id, join_timestamp) VALUES (?, ?, ?)',
                  (referrer_id, referred_id, now))
        conn.commit()
    except sqlite3.IntegrityError: pass
    conn.close()

def check_and_award_referrals():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor(); now = datetime.now()
    c.execute('SELECT id, referrer_id, referred_id, join_timestamp FROM pending_referrals')
    for pid, referrer_id, referred_id, join_ts in c.fetchall():
        join_time = datetime.fromisoformat(join_ts)
        if (now - join_time) >= timedelta(hours=REFERRAL_STAY_HOURS):
            try:
                member = bot.get_chat_member(f"@{CHANNEL_USERNAME}", referred_id)
                if member.status in ['member', 'administrator', 'creator']:
                    update_user_balance(referrer_id, REFERRAL_BONUS)
                    c.execute('INSERT INTO referrals (referrer_id, referred_id, join_timestamp, points_awarded, is_valid) VALUES (?, ?, ?, ?, 1)',
                              (referrer_id, referred_id, join_ts, REFERRAL_BONUS))
                    c.execute('DELETE FROM pending_referrals WHERE id = ?', (pid,))
                    conn.commit()
                    try: bot.send_message(referrer_id, f"🎉 Referral Bonus!\n\nYou earned +{REFERRAL_BONUS} Credits!")
                    except: pass
            except Exception as e: logger.error(f"Referral award error for pending {pid}: {e}")
    conn.close()

def get_referral_link(user_id):
    bot_username = bot.get_me().username
    return f"https://t.me/{bot_username}?start=ref_{user_id}"

def log_usage(user_id, module, details=""):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor(); now = datetime.now().isoformat()
    c.execute('INSERT INTO usage_logs (user_id, module, details, timestamp) VALUES (?, ?, ?, ?)',
              (user_id, module, details, now))
    c.execute('UPDATE users SET last_used = ? WHERE user_id = ?', (now, user_id))
    conn.commit(); conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT user_id, username, balance, status FROM users ORDER BY balance DESC')
    rows = c.fetchall(); conn.close(); return rows

def get_total_users():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor(); c.execute('SELECT COUNT(*) FROM users')
    count = c.fetchone()[0]; conn.close(); return count

def get_total_coins():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor(); c.execute('SELECT SUM(balance) FROM users')
    total = c.fetchone()[0]; conn.close(); return total if total else 0

def get_total_usage():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor(); c.execute('SELECT COUNT(*) FROM usage_logs')
    count = c.fetchone()[0]; conn.close(); return count

def get_config(key, default=None):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor(); c.execute('SELECT value FROM config WHERE key = ?', (key,))
    row = c.fetchone(); conn.close(); return row[0] if row else default

def set_config(key, value):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('REPLACE INTO config (key, value) VALUES (?, ?)', (key, value))
    conn.commit(); conn.close()

def get_module_cost(module):
    cost = get_config(f"{module}_cost")
    return int(cost) if cost else DEFAULT_COSTS.get(module, 1)

def get_yoga_refer_reward():
    return get_config("yoga_refer_reward", YOGA_REFER_REWARD)
def get_yoga_welcome_bonus():
    return get_config("yoga_welcome_bonus", YOGA_WELCOME_BONUS)

# ==================== YOGA API WITH PROXY ====================
def yoga_api_post(url, payload, headers):
    try:
        proxy_url = get_yoga_proxy_url()
        proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None
        resp = requests.post(url, json=payload, headers=headers, timeout=30, proxies=proxies)
        if resp.status_code in (200, 201):
            try: return resp.json(), None
            except: return None, "Invalid JSON response"
        return None, f"HTTP {resp.status_code}: {resp.text[:150]}"
    except Exception as e: return None, str(e)

def yoga_register(phone, code, name, did, sid):
    return yoga_api_post(YOGA_REGISTER_URL, {
        "name": name, "phoneNumber": phone, "referredBy": code,
        "sourceData": {"type": "Referral", "refererurl": "", "timezone": "Asia/Kolkata"},
        "experimentMetaInfo": {"deviceId": did, "sessionId": sid},
    }, YOGA_REG_HEADERS)

def yoga_send_otp(phone, did, sid):
    try:
        headers = {
            "accept": "application/json", "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json", "origin": "https://habit.yoga",
            "referer": "https://habit.yoga/", "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors", "sec-fetch-site": "cross-site",
            "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1",
        }
        payload = {
            "method": "phone_otp", "otpChannel": "sms", "phoneNumber": phone,
            "sourceData": {"type": "portal", "utm_source": "web_app"},
            "experimentMetaInfo": {"deviceId": did, "sessionId": sid}, "registerUser": False,
        }
        proxy_url = get_yoga_proxy_url()
        proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None
        resp = requests.post(YOGA_LOGIN_URL, json=payload, headers=headers, timeout=30, proxies=proxies)
        if resp.status_code in (200, 201):
            try:
                j = resp.json()
                if j.get("message") == "OTP sent to your phone":
                    ref = j.get("data", {}).get("refrence_code")
                    if ref: return ref, None
                return None, j.get("message", "Unknown error")
            except: return None, "Invalid JSON response"
        return None, f"HTTP {resp.status_code}: {resp.text[:150]}"
    except Exception as e: return None, str(e)

def yoga_verify_otp(phone, ref, otp, did, sid):
    return yoga_api_post(YOGA_VERIFY_URL, {
        "phone": phone, "reference_code": ref, "otp": otp,
        "experimentMetaInfo": {"deviceId": did, "sessionId": sid}, "registerUser": False,
    }, YOGA_HEADERS)

def rand_id(): return str(uuid.uuid4())
def rand_yoga_name(): return random.choice(YOGA_NAMES)

def extract_yoga_code(link):
    link = link.strip().rstrip("/")
    if "habit.yoga/" in link:
        code = link.replace("https://habit.yoga/", "").replace("http://habit.yoga/", "").split("/")[0]
        if code and all(c.isalnum() or c == "_" for c in code) and 1 <= len(code) <= 50: return code
        return None
    if link and all(c.isalnum() or c == "_" for c in link) and 1 <= len(link) <= 50: return link
    return None

# ==================== SHOPSY SESSION ====================
def save_shopsy_session(user_id, phone, session_data):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('REPLACE INTO shopsy_sessions (user_id, phone, session_data, updated_at) VALUES (?, ?, ?, ?)',
              (user_id, phone, json.dumps(session_data), datetime.now().isoformat()))
    conn.commit(); conn.close()
    set_shopsy_login_status(user_id, 1)

def get_shopsy_session(user_id):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT phone, session_data FROM shopsy_sessions WHERE user_id = ?', (user_id,))
    row = c.fetchone(); conn.close()
    if row: return row[0], json.loads(row[1])
    return None, None

def logout_shopsy_user(user_id):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('DELETE FROM shopsy_sessions WHERE user_id = ?', (user_id,))
    c.execute('UPDATE users SET shopsy_is_logged_in = 0 WHERE user_id=?', (user_id,))
    conn.commit(); conn.close(); return True

# ==================== MEMBERSHIP ====================
def is_channel_member(user_id):
    try:
        member = bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

def check_membership(user_id): return is_channel_member(user_id)

# ==================== GLOBAL STATES ====================
user_temp_sessions = {}
user_instagram_state = {}
user_firebase_state = {}
user_music_state = {}
user_shopsy_state = {}
user_shopsy_otp_data = {}
igviewer_data = {}
user_igviewer_state = {}
user_yoga_state = {}
user_yoga_otp_data = {}
user_flipkart_state = {}
user_supercoin_state = {}
user_supercoin_otp_data = {}

def back_button():
    kb = InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu"))
    return kb

def abort_kb(cancel_cb, back_cb):
    kb = InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton("❌ Abort", callback_data=cancel_cb))
    kb.row(InlineKeyboardButton("🔙 Back", callback_data=back_cb))
    return kb

# ==================== SHOPSY API WITH PROXY ====================
def generate_ids():
    return uuid.uuid4().hex[:32], f"{uuid.uuid4().hex[:32]}-{int(time.time() * 1000)}", f"{uuid.uuid4()}_{int(time.time()*1000)}"

def save_session(phone, session_data):
    with open(os.path.join(SHOPSY_SESSIONS_DIR, f"{phone}.json"), "w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=2, ensure_ascii=False)

def update_session(session_data, resp_json, resp_headers):
    if isinstance(resp_json, dict):
        sess = resp_json.get("SESSION") or resp_json.get("RESPONSE", {}).get("SESSION") or {}
        for k in ["accountId", "at", "rt", "sn", "secureToken", "nsid", "vid", "email", "firstName", "lastName"]:
            if sess.get(k): session_data[k] = sess[k]
        if session_data.get("firstName"):
            session_data["userName"] = f"{session_data.get('firstName', '')} {session_data.get('lastName', '')}".strip()
        if sess.get("isLoggedIn") is not None: session_data["isLoggedIn"] = sess["isLoggedIn"]
    if resp_headers:
        hl = {k.lower(): v for k, v in resp_headers.items()}
        for k in ["at", "rt", "sn", "nsid", "vid"]:
            if k in hl: session_data[k] = hl[k]
        if hl.get("securecookie"): session_data["secureCookie"] = hl.get("securecookie")
    return session_data

def sync_api_request(method, url_path, json_body, session_data, is_game=False):
    device_id = session_data.get("device_id") or uuid.uuid4().hex[:32]
    visit_id = session_data.get("visit_id") or f"{uuid.uuid4().hex[:32]}-{int(time.time() * 1000)}"
    app_sess = session_data.get("app_session_id") or f"{uuid.uuid4()}_{int(time.time()*1000)}"
    
    if is_game:
        headers = {
            "x-user-agent": f"Mozilla/5.0 (Linux; Android 9; OPPO:CPH2083 Build/{device_id[:13]}) FKUA/Retail/2291170/Android/Mobile (OPPO/OPPO:CPH2083/{device_id})",
            "sessionid": "session_id", "Content-Type": "application/json; charset=UTF-8",
            "User-Agent": "okhttp/4.9.2", "Accept-Encoding": "gzip", "Connection": "Keep-Alive", "city": "Delhi"
        }
    else:
        headers = {
            "X-PARTNER-CONTEXT": '{"source":"reseller"}', "FK-TENANT-ID": "SHOPSY",
            "business": "reseller", "Content-Type": "application/json; charset=UTF-8",
            "User-Agent": "okhttp/4.9.2",
            "X-User-Agent": f"Mozilla/5.0 (Linux; Android 9; CPH2083 Build/PPR1.180610.011) FKUA/Retail/2291170/Android/Mobile (OPPO/CPH2083/{device_id})",
            "X-Visit-Id": visit_id, "Accept-Encoding": "gzip", "Connection": "Keep-Alive",
            "city": "Delhi", "X-AppSession-ID": app_sess
        }
        for k in ["at", "sn", "secureToken"]:
            if session_data.get(k): headers[k] = session_data[k]
    
    sess = cffi_requests.Session(impersonate="chrome110")
    
    # Get proxy for Shopsy
    proxy_url = get_shopsy_proxy_url()
    proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None
    
    for attempt in range(1, 4):
        dc = session_data.get("current_dc", "1")
        url = f"https://{dc}.rome.api.flipkart.net{url_path}"
        try:
            if method == "POST":
                resp = sess.post(url, json=json_body, headers=headers, timeout=30, verify=False, proxies=proxies)
            else:
                resp = sess.get(url, headers=headers, timeout=30, verify=False, proxies=proxies)
            try: resp_json = resp.json()
            except: resp_json = {}
            if resp.status_code == 406 and resp_json.get("ERROR_MESSAGE") == "DC Change":
                new_dc = resp_json.get("RESPONSE", {}).get("id") or resp_json.get("RESPONSE", {}).get("dc")
                if new_dc: session_data["current_dc"] = str(new_dc); continue
            return resp.status_code, resp_json, dict(resp.headers), session_data
        except Exception as e:
            if attempt == 3: return 500, {"error": str(e)}, {}, session_data
            time.sleep(2)
    return 500, {"error": "Max retries"}, {}, session_data

async def run_sh_user_state(session_data):
    body = {
        "location": {"pincode": None},
        "ad": {"adId": str(uuid.uuid4()), "doNotPersonalizeAds": False, "sdkAdId": "", "adSdkVersion": "2.12.0"},
        "locale": {"deviceLanguage": "en", "shouldRefreshLanguage": False},
        "versions": {"cart": 1167987101, "userAccountState": 0, "abResponse": -2054295432,
            "abVariables": 0, "accountDetails": 1220048498, "wishlist": 0,
            "notifications": 861101, "location": 23273, "lockinResponse": 426889274}
    }
    st, rj, hdrs, session_data = await asyncio.to_thread(sync_api_request, "POST", "/4/user/state", body, session_data, False)
    return update_session(session_data, rj, hdrs)

async def get_user_info_tg(session_data):
    body = {"requestMethod": "GET", "routeUri": "user/get-user",
        "payload": {"userId": session_data.get("accountId", ""), "userName": session_data.get("userName", "User")}}
    st, rj, hdrs, session_data = await asyncio.to_thread(sync_api_request, "POST", "/1/shopsy/games", body, session_data, True)
    if st == 200 and isinstance(rj, dict) and rj.get("success"): return rj["data"]
    return None

async def get_config_tg(session_data):
    body = {"requestMethod": "GET", "routeUri": "config/get-config", "payload": {}}
    st, rj, hdrs, session_data = await asyncio.to_thread(sync_api_request, "POST", "/1/shopsy/games", body, session_data, True)
    if st == 200 and isinstance(rj, dict) and rj.get("success"): return rj["data"]
    return None

async def claim_gullak_tg(session_data):
    body = {"requestMethod": "POST", "routeUri": "gullak/claim-gullak",
        "payload": {"userId": session_data.get("accountId", "")}}
    await asyncio.to_thread(sync_api_request, "POST", "/1/shopsy/games", body, session_data, True)

async def start_game_tg(session_data, game_id):
    body = {"requestMethod": "POST", "routeUri": "game/game-started",
        "payload": {"userId": session_data.get("accountId", ""), "gameId": game_id}}
    st, rj, hdrs, session_data = await asyncio.to_thread(sync_api_request, "POST", "/1/shopsy/games", body, session_data, True)
    if st == 200 and isinstance(rj, dict) and rj.get("success"):
        return rj["data"].get("sessionId"), rj["data"]
    return None, rj

async def end_game_tg(session_data, game_id, game_session_id, play_time, gems_earned):
    body = {"requestMethod": "POST", "routeUri": "game/game-ended",
        "payload": {"userId": session_data.get("accountId", ""), "gameId": game_id,
            "sessionId": game_session_id, "gemsEarned": gems_earned, "playTimeInSec": play_time}}
    st, rj, hdrs, session_data = await asyncio.to_thread(sync_api_request, "POST", "/1/shopsy/games", body, session_data, True)
    if st == 200 and isinstance(rj, dict) and rj.get("success"): return rj["data"]
    return None

async def login_with_otp(phone):
    d_id, v_id, s_id = generate_ids()
    sd = {"phone": phone, "device_id": d_id, "visit_id": v_id,
        "app_session_id": s_id, "current_dc": "1", "owner_id": "telegram_bot", "last_refresh": time.time()}
    body = {"actionRequestContext": {
        "type": "LOGIN_IDENTITY_VERIFY_SHOPSY2", "loginId": phone,
        "loginIdPrefix": "+91", "phoneNumberFormat": "E164", "addAppHash": True,
        "loginType": "MOBILE", "verificationType": "OTP", "sourceContext": "DEFAULT",
        "clientQueryParamMap": None}}
    st, resp, hdrs, sd = await asyncio.to_thread(sync_api_request, "POST", "/1/action/view", body, sd, False)
    if st != 200 or not isinstance(resp, dict): return None, f"OTP request failed (HTTP {st})"
    sd = update_session(sd, resp, hdrs)
    req_id = resp.get("RESPONSE", {}).get("actionResponseContext", {}).get("requestId") or resp.get("requestId")
    if not req_id: return None, "No request ID in response"
    sd["otpRequestId"] = req_id; return sd, "OTP sent"

async def verify_otp(session_data, otp):
    phone = session_data.get("phone")
    body = {"actionRequestContext": {
        "type": "LOGIN_SHOPSY2", "loginId": phone, "loginIdPrefix": "+91",
        "password": None, "otp": otp, "otpRequestId": session_data.get("otpRequestId"),
        "remainingAttempts": 5, "phoneNumberFormat": "E164", "loginType": "MOBILE",
        "verificationType": "OTP", "sourceContext": "DEFAULT", "churned": False}}
    st, resp, hdrs, sd = await asyncio.to_thread(sync_api_request, "POST", "/1/action/view", body, session_data, False)
    if st == 200 and isinstance(resp, dict) and resp.get("RESPONSE", {}).get("actionResponseContext", {}).get("authenticationSuccess", False):
        sd = update_session(sd, resp, hdrs); sd["isLoggedIn"] = True; sd["last_refresh"] = time.time()
        return sd, True
    return session_data, False

async def refresh_session_once(session_data):
    phone = session_data.get("phone")
    try:
        session_data = await run_sh_user_state(session_data)
        session_data["last_refresh"] = time.time()
        save_session(phone, session_data); return session_data
    except: return session_data

async def core_mine_logic(session_data, progress_callback=None):
    phone = session_data.get("phone")
    if progress_callback: await progress_callback("🔄 Refreshing session...")
    session_data = await refresh_session_once(session_data)
    if progress_callback: await progress_callback("🔄 Fetching user state...")
    session_data = await run_sh_user_state(session_data)
    save_session(phone, session_data)
    if progress_callback: await progress_callback("💰 Getting balance...")
    iud = await get_user_info_tg(session_data)
    if not iud: return {"status": "fail", "earned": 0, "msg": "Session expired. Please re-login."}
    ic = iud.get("earnings", {}).get("coinsEarnedTotal", 0)
    if progress_callback: await progress_callback("🎁 Claiming gullak...")
    await claim_gullak_tg(session_data)
    if progress_callback: await progress_callback("🎮 Fetching available games...")
    cd = await get_config_tg(session_data)
    games = cd.get("games", []) if cd else []
    if not games: return {"status": "fail", "earned": 0, "msg": "No active games"}
    played_count = 0; total_gems = 0; wait = 0
    for i, g in enumerate(games):
        game_id = g.get("id"); game_name = g.get("name", game_id)
        if progress_callback: await progress_callback(f"🎮 Starting {game_name} ({i+1}/{len(games)})...")
        gsid, _ = await start_game_tg(session_data, game_id)
        if gsid:
            wait = random.randint(10, 13)
            for sec in range(wait, 0, -1):
                if progress_callback and sec % 3 == 0:
                    await progress_callback(f"⏳ Playing {game_name}... {sec}s remaining")
                await asyncio.sleep(1)
            gems = random.randint(3000, 5000)
            ed = await end_game_tg(session_data, game_id, gsid, wait, gems)
            if ed: played_count += 1; total_gems += gems
            if progress_callback: await progress_callback(f"✅ Earned {gems} gems from {game_name}" if ed else f"⚠️ Failed to complete {game_name}")
        else:
            if progress_callback: await progress_callback(f"❌ Could not start {game_name}")
        await asyncio.sleep(0.5)
    save_session(phone, session_data)
    if progress_callback: await progress_callback("📊 Finalizing balance...")
    fud = await get_user_info_tg(session_data)
    fc = fud.get("earnings", {}).get("coinsEarnedTotal", 0) if fud else ic
    earned = max(0, fc - ic)
    return {"status": "success", "earned": earned, "final_coins": fc,
        "played": played_count, "total": len(games), "gems": total_gems,
        "time_taken": (wait * len(games)) if len(games) > 0 else 0}

async def fetch_supercoin_data(session_data):
    session_data = await refresh_session_once(session_data)
    ud = await get_user_info_tg(session_data)
    if not ud: return None, "Could not fetch user data"
    e = ud.get("earnings", {})
    return {"coins_earned": e.get("coinsEarnedTotal", 0), "daily_coins": e.get("dailyCoinsEarned", 0),
        "weekly_coins": e.get("weeklyCoinsEarned", 0), "user_name": ud.get("userName", "User")}, None

# ==================== FIREBASE SCANNER ====================
def scan_apk_for_firebase(apk_path):
    results = {"firebase_urls": [], "api_keys": [], "secrets": [], "storage_buckets": [], "json_endpoints": []}
    fb_pats = [
        r'https?://[a-zA-Z0-9_.-]+\.firebaseio\.com',
        r'https?://[a-zA-Z0-9_.-]+\.firebaseapp\.com',
        r'https?://[a-zA-Z0-9_.-]+\.firebasestorage\.app',
        r'https?://[a-zA-Z0-9_.-]+\.appspot\.com',
        r'https?://[a-zA-Z0-9_.-]+\.googleapis\.com',
    ]
    api_key_pat = r'AIza[0-9A-Za-z_-]{35}'
    sec_pats = [
        r'(?:api|secret|token|key|password|auth)[:=]\s*["'']?([^"'']{8,})["'']?',
        r'(?:bearer|access_token|refresh_token)[:=]\s*["'']?([^"'']{8,})["'']?',
    ]
    json_pat = r'https?://[a-zA-Z0-9_.-]+/[a-zA-Z0-9_/.-]+\.json'
    try:
        with zipfile.ZipFile(apk_path, 'r') as zf:
            for fname in zf.namelist():
                if fname.startswith('res/') or fname.endswith(('.png','.jpg','.mp3','.wav')): continue
                try:
                    text = zf.read(fname).decode('utf-8', errors='ignore')
                    for p in fb_pats:
                        for m in re.findall(p, text, re.IGNORECASE):
                            if m not in results["firebase_urls"]: results["firebase_urls"].append(m)
                    for m in re.findall(api_key_pat, text):
                        if m not in results["api_keys"]: results["api_keys"].append(m)
                    for pat in sec_pats:
                        for m in re.findall(pat, text, re.IGNORECASE):
                            val = m[0] if isinstance(m, tuple) else m
                            if val and len(val) > 8 and val not in results["secrets"]: results["secrets"].append(val)
                    for m in re.findall(json_pat, text, re.IGNORECASE):
                        if m not in results["json_endpoints"]: results["json_endpoints"].append(m)
                    for m in re.findall(r'[a-zA-Z0-9_-]+\.appspot\.com', text):
                        if m not in results["storage_buckets"]: results["storage_buckets"].append(m)
                except: continue
    except Exception as e: raise Exception(f"Error scanning APK: {str(e)}")
    return results

# ==================== TEMP MAIL API ====================
TEMP_MAIL_API = "https://api.mail.tm"

def create_temp_email():
    try:
        resp = requests.get(f"{TEMP_MAIL_API}/domains", timeout=10)
        if resp.status_code != 200: return None, "Could not fetch domains"
        domains = resp.json().get("hydra:member", [])
        if not domains: return None, "No domains available"
        domain = domains[0]["domain"]
        email = f"{''.join(random.choices(string.ascii_lowercase, k=10))}@{domain}"
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        resp = requests.post(f"{TEMP_MAIL_API}/accounts", json={"address": email, "password": password},
            headers={"Content-Type": "application/json"}, timeout=10)
        if resp.status_code not in (200, 201): return None, f"Account creation failed: HTTP {resp.status_code}"
        tresp = requests.post(f"{TEMP_MAIL_API}/token", json={"address": email, "password": password},
            headers={"Content-Type": "application/json"}, timeout=10)
        if tresp.status_code != 200: return None, "Token generation failed"
        return {"email": email, "password": password, "token": tresp.json().get("token")}, None
    except Exception as e: return None, str(e)

def get_temp_mail_messages(token):
    try:
        resp = requests.get(f"{TEMP_MAIL_API}/messages", headers={"Authorization": f"Bearer {token}"}, timeout=10)
        if resp.status_code != 200: return None, f"Failed: HTTP {resp.status_code}"
        return resp.json().get("hydra:member", []), None
    except Exception as e: return None, str(e)

def get_temp_message_content(token, msg_id):
    try:
        resp = requests.get(f"{TEMP_MAIL_API}/messages/{msg_id}", headers={"Authorization": f"Bearer {token}"}, timeout=10)
        if resp.status_code != 200: return None, f"Failed: HTTP {resp.status_code}"
        return resp.json(), None
    except Exception as e: return None, str(e)

def extract_otp_from_message(msg):
    text = ""
    if msg.get("html"): text = re.sub(r'<[^>]+>', ' ', msg["html"])
    if msg.get("text"): text += " " + msg["text"]
    for pat in [r'(?:OTP|otp|Otp)[:\s]*(\d{4,8})', r'(?:code|Code|CODE)[:\s]*(\d{4,8})',
                r'(?:verification|Verification)[:\s]*(\d{4,8})', r'(?:one.?time|One.?Time)[:\s]*(\d{4,8})',
                r'(\d{4,8})(?:\s|$|\.)']:
        m = re.search(pat, text)
        if m:
            c = (m.group(1) if m.lastindex else m.group(0)).strip()
            if len(c) >= 4 and len(c) <= 8 and c.isdigit(): return c
    return None

def delete_temp_email(token):
    try:
        resp = requests.delete(f"{TEMP_MAIL_API}/me", headers={"Authorization": f"Bearer {token}"}, timeout=10)
        return resp.status_code in (200, 201, 204)
    except: return False

# ==================== FLIPKART CHECKER WITH PROXY ====================
def check_flipkart_number(phone):
    try:
        proxy_url = get_flipkart_proxy_url()
        proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None
        
        resp = requests.post(
            "https://1.rome.api.flipkart.com/api/6/user/signup/status",
            json={"loginId": phone, "loginIdPrefix": "+91"},
            headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G975F)",
                "FK-TENANT-ID": "FLIPKART", "X-Request-Id": str(uuid.uuid4())}, 
            timeout=15,
            proxies=proxies
        )
        if resp.status_code == 200:
            d = resp.json()
            s = d.get("status", "UNKNOWN")
            return s if s in ("VERIFIED", "GUEST") else s, None
        elif resp.status_code in (403, 429): return None, "API_BLOCKED"
        else: return None, f"HTTP {resp.status_code}"
    except Exception as e: return None, str(e)

# ==================== IG VIEWER ====================
def fetch_ig_profile(username):
    try:
        resp = requests.get(f"https://storyviewer.com/api/v1/web/profile/{username}",
            headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"}, timeout=15)
        if resp.status_code == 200: return resp.json(), None
        else: return None, f"HTTP {resp.status_code}"
    except Exception as e: return None, str(e)

# ==================== MUSIC DOWNLOADER ====================
def search_music_youtube(query):
    if not YT_DLP_AVAILABLE: return None, "yt-dlp not installed. Run: pip install yt-dlp"
    try:
        with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True, 'extract_flat': True}) as ydl:
            result = ydl.extract_info(f"ytsearch5:{query} audio", download=False)
            if not result or 'entries' not in result: return None, "No results found"
            entries = []
            for e in result['entries']:
                if e:
                    entries.append({'id': e.get('id'), 'title': e.get('title', 'Unknown'),
                        'url': f"https://youtube.com/watch?v={e.get('id')}",
                        'duration': e.get('duration', 0), 'uploader': e.get('uploader', 'Unknown')})
            return entries, None
    except Exception as e: return None, str(e)

def download_youtube_audio(video_url, output_dir):
    if not YT_DLP_AVAILABLE: return None, "yt-dlp not installed"
    try:
        with yt_dlp.YoutubeDL({'format': 'bestaudio/best',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '320'}],
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'quiet': True, 'no_warnings': True}) as ydl:
            info = ydl.extract_info(video_url, download=True)
            title = info.get('title', 'audio')
            fp = os.path.join(output_dir, f"{title}.mp3")
            if os.path.exists(fp): return fp, None
            for f in os.listdir(output_dir):
                if f.endswith('.mp3'): return os.path.join(output_dir, f), None
            return None, "Download failed"
    except Exception as e: return None, str(e)

# ==================== SHOPSY HANDLERS ====================
@bot.message_handler(func=lambda m: user_shopsy_state.get(m.from_user.id) == "waiting_phone")
def shopsy_phone_handler(message):
    uid = message.from_user.id; phone = message.text.strip()
    if phone.lower() in ['/cancel', 'cancel', 'abort']:
        user_shopsy_state[uid] = None; bot.reply_to(message, "❌ Shopsy mining cancelled.", reply_markup=back_button()); return
    if not phone.isdigit() or len(phone) != 10:
        bot.reply_to(message, "❌ Please enter exactly 10 digits.\n\nSend /cancel to abort."); return
    cost = get_module_cost("shopsy")
    if get_user_balance(uid) < cost:
        bot.reply_to(message, f"❌ Insufficient credits! Need {cost} credits. Balance: {get_user_balance(uid)}"); return
    kb = InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton("❌ Abort", callback_data="shopsy_abort"))
    kb.row(InlineKeyboardButton("🔙 Back", callback_data="back_shopsy"))
    sm = bot.reply_to(message, f"📱 Sending OTP to +91{phone}...", reply_markup=kb)
    update_user_balance(uid, -cost)
    def thread():
        try:
            loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
            sd, msg = loop.run_until_complete(login_with_otp(phone)); loop.close()
            if not sd:
                update_user_balance(uid, cost)
                bot.edit_message_text(f"❌ Failed: {msg}", chat_id=message.chat.id, message_id=sm.message_id, reply_markup=back_button())
                user_shopsy_state[uid] = None; return
            user_shopsy_otp_data[uid] = {"session_data": sd, "phone": phone, "cost": cost}
            user_shopsy_state[uid] = "waiting_otp"
            okb = InlineKeyboardMarkup()
            okb.row(InlineKeyboardButton("❌ Abort", callback_data="shopsy_abort_otp"))
            okb.row(InlineKeyboardButton("🔙 Back", callback_data="back_shopsy"))
            bot.edit_message_text(f"✅ OTP sent to +91{phone}!\n\nEnter the OTP code:\n\nSend /cancel to abort.",
                chat_id=message.chat.id, message_id=sm.message_id, reply_markup=okb)
        except Exception as e:
            update_user_balance(uid, cost)
            bot.edit_message_text(f"❌ Error: {str(e)[:200]}", chat_id=message.chat.id, message_id=sm.message_id, reply_markup=back_button())
            user_shopsy_state[uid] = None
    threading.Thread(target=thread).start()

@bot.message_handler(func=lambda m: user_shopsy_state.get(m.from_user.id) == "waiting_otp")
def shopsy_otp_handler(message):
    uid = message.from_user.id; otp = message.text.strip()
    if otp.lower() in ['/cancel', 'cancel']:
        user_shopsy_state[uid] = None
        if uid in user_shopsy_otp_data: update_user_balance(uid, user_shopsy_otp_data[uid]["cost"]); del user_shopsy_otp_data[uid]
        bot.reply_to(message, "❌ Shopsy login cancelled.", reply_markup=back_button()); return
    if not otp.isdigit() or len(otp) != 6:
        bot.reply_to(message, "❌ Please enter a valid 6-digit OTP.\n\nSend /cancel to abort."); return
    if uid not in user_shopsy_otp_data:
        bot.reply_to(message, "❌ Session expired. Please start again."); user_shopsy_state[uid] = None; return
    d = user_shopsy_otp_data[uid]; sd = d["session_data"]; phone = d["phone"]; cost = d["cost"]
    sm = bot.reply_to(message, "🔄 Verifying OTP...")
    def thread():
        try:
            loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
            us, ok = loop.run_until_complete(verify_otp(sd, otp)); loop.close()
            if ok:
                save_shopsy_session(uid, phone, us); update_user_balance(uid, cost)
                bot.edit_message_text(f"✅ Shopsy Login Successful!\n\n📱 +91{phone}\n💰 Refunded: +{cost} credits\n💳 Balance: {get_user_balance(uid)}\n\n🎮 Start mining from Shopsy menu!",
                    chat_id=message.chat.id, message_id=sm.message_id, reply_markup=back_button())
                user_shopsy_state[uid] = None
                if uid in user_shopsy_otp_data: del user_shopsy_otp_data[uid]
            else:
                update_user_balance(uid, cost)
                bot.edit_message_text("❌ Invalid OTP. Try again.\n\nSend /cancel to abort.", chat_id=message.chat.id, message_id=sm.message_id)
                user_shopsy_state[uid] = "waiting_otp"
        except Exception as e:
            update_user_balance(uid, cost)
            bot.edit_message_text(f"❌ Error: {str(e)[:200]}", chat_id=message.chat.id, message_id=sm.message_id, reply_markup=back_button())
            user_shopsy_state[uid] = None
            if uid in user_shopsy_otp_data: del user_shopsy_otp_data[uid]
    threading.Thread(target=thread).start()

# ==================== SUPERCOIN HANDLERS ====================
@bot.message_handler(func=lambda m: user_supercoin_state.get(m.from_user.id) == "waiting_supercoin_phone")
def supercoin_phone_handler(message):
    uid = message.from_user.id; phone = message.text.strip()
    if phone.lower() in ['/cancel', 'cancel', 'abort']:
        user_supercoin_state[uid] = None; bot.reply_to(message, "❌ Supercoin fetch cancelled.", reply_markup=back_button()); return
    if not phone.isdigit() or len(phone) != 10:
        bot.reply_to(message, "❌ Please enter exactly 10 digits.\n\nSend /cancel to abort."); return
    cost = get_module_cost("supercoin")
    if get_user_balance(uid) < cost:
        bot.reply_to(message, f"❌ Insufficient credits! Need {cost} credits. Balance: {get_user_balance(uid)}"); return
    update_user_balance(uid, -cost)
    kb = InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton("❌ Abort", callback_data="supercoin_abort"))
    kb.row(InlineKeyboardButton("🔙 Back", callback_data="back_menu"))
    sm = bot.reply_to(message, f"📱 Sending OTP to +91{phone}...", reply_markup=kb)
    def thread():
        try:
            loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
            sd, msg = loop.run_until_complete(login_with_otp(phone)); loop.close()
            if not sd:
                update_user_balance(uid, cost)
                bot.edit_message_text(f"❌ Failed: {msg}", chat_id=message.chat.id, message_id=sm.message_id, reply_markup=back_button())
                user_supercoin_state[uid] = None; return
            user_supercoin_otp_data[uid] = {"session_data": sd, "phone": phone, "cost": cost}
            user_supercoin_state[uid] = "waiting_supercoin_otp"
            okb = InlineKeyboardMarkup()
            okb.row(InlineKeyboardButton("❌ Abort", callback_data="supercoin_abort_otp"))
            okb.row(InlineKeyboardButton("🔙 Back", callback_data="back_menu"))
            bot.edit_message_text(f"✅ OTP sent to +91{phone}!\n\nEnter the OTP code:\n\nSend /cancel to abort.",
                chat_id=message.chat.id, message_id=sm.message_id, reply_markup=okb)
        except Exception as e:
            update_user_balance(uid, cost)
            bot.edit_message_text(f"❌ Error: {str(e)[:200]}", chat_id=message.chat.id, message_id=sm.message_id, reply_markup=back_button())
            user_supercoin_state[uid] = None
    threading.Thread(target=thread).start()

@bot.message_handler(func=lambda m: user_supercoin_state.get(m.from_user.id) == "waiting_supercoin_otp")
def supercoin_otp_handler(message):
    uid = message.from_user.id; otp = message.text.strip()
    if otp.lower() in ['/cancel', 'cancel']:
        user_supercoin_state[uid] = None
        if uid in user_supercoin_otp_data: update_user_balance(uid, user_supercoin_otp_data[uid]["cost"]); del user_supercoin_otp_data[uid]
        bot.reply_to(message, "❌ Supercoin fetch cancelled.", reply_markup=back_button()); return
    if not otp.isdigit() or len(otp) != 6:
        bot.reply_to(message, "❌ Please enter a valid 6-digit OTP.\n\nSend /cancel to abort."); return
    if uid not in user_supercoin_otp_data:
        bot.reply_to(message, "❌ Session expired. Please start again."); user_supercoin_state[uid] = None; return
    d = user_supercoin_otp_data[uid]; sd = d["session_data"]; phone = d["phone"]; cost = d["cost"]
    sm = bot.reply_to(message, "🔄 Verifying OTP...")
    def thread():
        try:
            loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
            us, ok = loop.run_until_complete(verify_otp(sd, otp))
            if ok:
                bd, err = loop.run_until_complete(fetch_supercoin_data(us)); loop.close()
                update_user_balance(uid, cost)
                if bd:
                    bot.edit_message_text(f"✅ Supercoin Balance\n\n👤 {bd['user_name']}\n📱 +91{phone}\n\n💰 Total: {bd['coins_earned']}\n📅 Daily: {bd['daily_coins']}\n📆 Weekly: {bd['weekly_coins']}\n\n💳 Bot Balance: {get_user_balance(uid)} Credits",
                        chat_id=message.chat.id, message_id=sm.message_id, reply_markup=back_button())
                else:
                    bot.edit_message_text(f"✅ Login Successful!\n\n📱 +91{phone}\n⚠️ Could not fetch supercoin data.\n💳 Balance: {get_user_balance(uid)}",
                        chat_id=message.chat.id, message_id=sm.message_id, reply_markup=back_button())
            else:
                loop.close(); update_user_balance(uid, cost)
                bot.edit_message_text("❌ Invalid OTP. Try again.", chat_id=message.chat.id, message_id=sm.message_id)
                user_supercoin_state[uid] = "waiting_supercoin_otp"
            user_supercoin_state[uid] = None
            if uid in user_supercoin_otp_data: del user_supercoin_otp_data[uid]
        except Exception as e:
            loop.close(); update_user_balance(uid, cost)
            bot.edit_message_text(f"❌ Error: {str(e)[:200]}", chat_id=message.chat.id, message_id=sm.message_id, reply_markup=back_button())
            user_supercoin_state[uid] = None
            if uid in user_supercoin_otp_data: del user_supercoin_otp_data[uid]
    threading.Thread(target=thread).start()

# ==================== YOGA HANDLERS ====================
@bot.message_handler(func=lambda m: user_yoga_state.get(m.from_user.id) == "waiting_yoga_phone")
def yoga_phone_handler(message):
    uid = message.from_user.id; phone = message.text.strip()
    if phone.lower() in ['/cancel', 'cancel']:
        user_yoga_state[uid] = None; bot.reply_to(message, "❌ Yoga referral cancelled.", reply_markup=back_button()); return
    if not phone.isdigit() or len(phone) != 10:
        bot.reply_to(message, "❌ Please enter exactly 10 digits.\n\nSend /cancel to abort."); return
    cost = get_module_cost("yoga")
    if get_user_balance(uid) < cost:
        bot.reply_to(message, f"❌ Insufficient credits! Need {cost} credits. Balance: {get_user_balance(uid)}"); return
    user_yoga_state[uid] = "waiting_yoga_otp"
    kb = InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton("❌ Abort", callback_data="yoga_abort_otp"))
    kb.row(InlineKeyboardButton("🔙 Back", callback_data="back_yoga"))
    sm = bot.reply_to(message, f"📱 Sending OTP to +91{phone}...", reply_markup=kb)
    update_user_balance(uid, -cost)
    def thread():
        try:
            did = rand_id(); sid = rand_id()
            ref, err = yoga_send_otp(phone, did, sid)
            if err:
                update_user_balance(uid, cost)
                bot.edit_message_text(f"❌ Failed to send OTP: {err}", chat_id=message.chat.id, message_id=sm.message_id, reply_markup=back_button())
                user_yoga_state[uid] = None; return
            user_yoga_otp_data[uid] = {"phone": phone, "ref": ref, "did": did, "sid": sid, "cost": cost}
            okb = InlineKeyboardMarkup()
            okb.row(InlineKeyboardButton("❌ Abort", callback_data="yoga_abort_otp"))
            okb.row(InlineKeyboardButton("🔙 Back", callback_data="back_yoga"))
            bot.edit_message_text(f"✅ OTP sent to +91{phone}!\n\nEnter the 6-digit OTP:\n\nSend /cancel to abort.",
                chat_id=message.chat.id, message_id=sm.message_id, reply_markup=okb)
            user_yoga_state[uid] = "waiting_yoga_otp"
        except Exception as e:
            update_user_balance(uid, cost)
            bot.edit_message_text(f"❌ Error: {str(e)[:200]}", chat_id=message.chat.id, message_id=sm.message_id, reply_markup=back_button())
            user_yoga_state[uid] = None
    threading.Thread(target=thread).start()

@bot.message_handler(func=lambda m: user_yoga_state.get(m.from_user.id) == "waiting_yoga_otp")
def yoga_otp_handler(message):
    uid = message.from_user.id; otp = message.text.strip()
    if otp.lower() in ['/cancel', 'cancel']:
        user_yoga_state[uid] = None
        if uid in user_yoga_otp_data: del user_yoga_otp_data[uid]
        bot.reply_to(message, "❌ Yoga referral cancelled.", reply_markup=back_button()); return
    if not otp.isdigit() or len(otp) != 6:
        bot.reply_to(message, "❌ Please enter a valid 6-digit OTP.\n\nSend /cancel to abort."); return
    if uid not in user_yoga_otp_data:
        bot.reply_to(message, "❌ Session expired. Start again."); user_yoga_state[uid] = None; return
    d = user_yoga_otp_data[uid]; phone = d["phone"]; ref = d["ref"]; did = d["did"]; sid = d["sid"]; cost = d["cost"]
    sm = bot.reply_to(message, "🔄 Verifying OTP...")
    def thread():
        try:
            resp, err = yoga_verify_otp(phone, ref, otp, did, sid)
            if err:
                update_user_balance(uid, cost)
                bot.edit_message_text(f"❌ OTP verification failed: {err}", chat_id=message.chat.id, message_id=sm.message_id, reply_markup=back_button())
                user_yoga_state[uid] = None; cleanup(); return
            if resp and resp.get("data", {}).get("isVerified", False):
                conn = sqlite3.connect(DB_PATH, check_same_thread=False)
                c = conn.cursor(); c.execute('SELECT yoga_code FROM users WHERE user_id = ?', (uid,))
                row = c.fetchone(); conn.close()
                yoga_code = row[0] if row and row[0] else None
                if not yoga_code:
                    update_user_balance(uid, cost)
                    bot.edit_message_text("⚠️ Yoga referral code not set!\n\nUse /setyoga YOUR_CODE", chat_id=message.chat.id, message_id=sm.message_id, reply_markup=back_button())
                    user_yoga_state[uid] = None; cleanup(); return
                name = rand_yoga_name()
                reg_resp, reg_err = yoga_register(phone, yoga_code, name, did, sid)
                if reg_err:
                    update_user_balance(uid, cost)
                    bot.edit_message_text(f"❌ Registration failed: {reg_err}", chat_id=message.chat.id, message_id=sm.message_id, reply_markup=back_button())
                    user_yoga_state[uid] = None; cleanup(); return
                reward = get_yoga_refer_reward()
                update_user_balance(uid, reward)
                conn = sqlite3.connect(DB_PATH, check_same_thread=False)
                c = conn.cursor()
                c.execute('UPDATE users SET yoga_bot_refers = yoga_bot_refers + 1 WHERE user_id = ?', (uid,))
                conn.commit(); conn.close()
                bot.edit_message_text(f"✅ Yoga Referral Successful!\n\n📱 +91{phone}\n👤 {name}\n🔑 Code: {yoga_code}\n💰 +{reward} Credits\n💳 New: {get_user_balance(uid)}",
                    chat_id=message.chat.id, message_id=sm.message_id, reply_markup=back_button())
                user_yoga_state[uid] = None; cleanup()
            else:
                update_user_balance(uid, cost)
                bot.edit_message_text("❌ OTP verification failed.", chat_id=message.chat.id, message_id=sm.message_id, reply_markup=back_button())
                user_yoga_state[uid] = None; cleanup()
        except Exception as e:
            update_user_balance(uid, cost)
            bot.edit_message_text(f"❌ Error: {str(e)[:200]}", chat_id=message.chat.id, message_id=sm.message_id, reply_markup=back_button())
            user_yoga_state[uid] = None; cleanup()
    def cleanup():
        if uid in user_yoga_otp_data: del user_yoga_otp_data[uid]
    threading.Thread(target=thread).start()

# ==================== FLIPKART HANDLER ====================
@bot.message_handler(func=lambda m: user_flipkart_state.get(m.from_user.id) == "waiting_flipkart_number")
def flipkart_number_handler(message):
    uid = message.from_user.id; phone = message.text.strip()
    if phone.lower() in ['/cancel', 'cancel']:
        user_flipkart_state[uid] = None; bot.reply_to(message, "❌ Flipkart check cancelled.", reply_markup=back_button()); return
    if not phone.isdigit() or len(phone) != 10:
        bot.reply_to(message, "❌ Please enter exactly 10 digits.\n\nSend /cancel to abort."); return
    cost = get_module_cost("flipkart")
    if get_user_balance(uid) < cost:
        bot.reply_to(message, f"❌ Insufficient credits! Need {cost} credits. Balance: {get_user_balance(uid)}"); return
    update_user_balance(uid, -cost); user_flipkart_state[uid] = None
    sm = bot.reply_to(message, f"🔍 Checking +91{phone} on Flipkart...")
    def thread():
        try:
            status, err = check_flipkart_number(phone)
            if err:
                update_user_balance(uid, cost)
                txt = f"⚠️ API Blocked\n\n📱 +91{phone}\nTry again later." if err == "API_BLOCKED" else f"❌ Error: {err}"
                bot.edit_message_text(txt, chat_id=message.chat.id, message_id=sm.message_id, reply_markup=back_button()); return
            log_usage(uid, "flipkart", f"Checked {phone}: {status}")
            if status == "VERIFIED": txt = f"✅ VERIFIED\n\n📱 +91{phone} is registered on Flipkart!"
            elif status == "GUEST": txt = f"❌ GUEST\n\n📱 +91{phone} is NOT registered on Flipkart."
            else: txt = f"❓ Status: {status}\n\n📱 +91{phone}"
            bot.edit_message_text(txt, chat_id=message.chat.id, message_id=sm.message_id, reply_markup=back_button())
        except Exception as e:
            update_user_balance(uid, cost)
            bot.edit_message_text(f"❌ Error: {str(e)[:200]}", chat_id=message.chat.id, message_id=sm.message_id, reply_markup=back_button())
    threading.Thread(target=thread).start()

# ==================== INSTAGRAM HANDLERS ====================
@bot.message_handler(func=lambda m: user_instagram_state.get(m.from_user.id) == "waiting_instagram_single")
def instagram_single_handler(message):
    uid = message.from_user.id; url = message.text.strip()
    if url.lower() in ['/cancel', 'cancel']:
        user_instagram_state[uid] = None; bot.reply_to(message, "❌ Instagram download cancelled.", reply_markup=back_button()); return
    cost = get_module_cost("instagram_single")
    if get_user_balance(uid) < cost:
        bot.reply_to(message, f"❌ Insufficient credits! Need {cost} credits. Balance: {get_user_balance(uid)}"); return
    update_user_balance(uid, -cost); user_instagram_state[uid] = None
    sm = bot.reply_to(message, "🔄 Downloading reel..."); tmpdir = tempfile.mkdtemp()
    def thread():
        try:
            L = instaloader.Instaloader(dirname_pattern=tmpdir, quiet=True, download_video_thumbnails=False, download_comments=False, save_metadata=False, compress_json=False)
            sc = None
            if "instagram.com/reel/" in url: sc = url.split("/reel/")[1].split("/")[0].split("?")[0]
            elif "instagram.com/p/" in url: sc = url.split("/p/")[1].split("/")[0].split("?")[0]
            if not sc:
                shutil.rmtree(tmpdir, ignore_errors=True); update_user_balance(uid, cost)
                bot.edit_message_text("❌ Invalid Instagram URL.", chat_id=message.chat.id, message_id=sm.message_id, reply_markup=back_button()); return
            post = instaloader.Post.from_shortcode(L.context, sc)
            L.download_post(post, target=tmpdir)
            vf = None
            for f in os.listdir(tmpdir):
                if f.endswith('.mp4'): vf = os.path.join(tmpdir, f); break
            if vf and os.path.getsize(vf) < 50 * 1024 * 1024:
                with open(vf, 'rb') as f: bot.send_video(uid, f, caption=f"✅ Downloaded by @{bot.get_me().username}", timeout=120)
                bot.edit_message_text("✅ Download complete!", chat_id=message.chat.id, message_id=sm.message_id, reply_markup=back_button())
                log_usage(uid, "instagram_single", f"Downloaded {sc}")
            else:
                update_user_balance(uid, cost)
                bot.edit_message_text("❌ Could not download video.", chat_id=message.chat.id, message_id=sm.message_id, reply_markup=back_button())
            shutil.rmtree(tmpdir, ignore_errors=True)
        except Exception as e:
            shutil.rmtree(tmpdir, ignore_errors=True); update_user_balance(uid, cost)
            bot.edit_message_text(f"❌ Error: {str(e)[:200]}", chat_id=message.chat.id, message_id=sm.message_id, reply_markup=back_button())
    threading.Thread(target=thread).start()

@bot.message_handler(func=lambda m: user_instagram_state.get(m.from_user.id) == "waiting_instagram_bulk")
def instagram_bulk_handler(message):
    uid = message.from_user.id; text = message.text.strip()
    if text.lower() in ['/cancel', 'cancel']:
        user_instagram_state[uid] = None; bot.reply_to(message, "❌ Bulk download cancelled.", reply_markup=back_button()); return
    urls = [u.strip() for u in text.split('\n') if u.strip()]
    cp = get_module_cost("instagram_bulk"); tc = cp * len(urls)
    if get_user_balance(uid) < tc:
        bot.reply_to(message, f"❌ Insufficient credits! Need {tc} for {len(urls)} videos. Balance: {get_user_balance(uid)}"); return
    update_user_balance(uid, -tc); user_instagram_state[uid] = None
    sm = bot.reply_to(message, f"🔄 Downloading {len(urls)} reels..."); tmpdir = tempfile.mkdtemp()
    def thread():
        s = 0; f = 0
        try:
            L = instaloader.Instaloader(dirname_pattern=tmpdir, quiet=True, download_video_thumbnails=False, download_comments=False, save_metadata=False, compress_json=False)
            for i, url in enumerate(urls):
                try:
                    sc = None
                    if "instagram.com/reel/" in url: sc = url.split("/reel/")[1].split("/")[0].split("?")[0]
                    elif "instagram.com/p/" in url: sc = url.split("/p/")[1].split("/")[0].split("?")[0]
                    if not sc: f += 1; continue
                    post = instaloader.Post.from_shortcode(L.context, sc)
                    L.download_post(post, target=tmpdir)
                    vf = None
                    for ff in os.listdir(tmpdir):
                        if ff.endswith('.mp4'): vf = os.path.join(tmpdir, ff); break
                    if vf and os.path.getsize(vf) < 50*1024*1024:
                        with open(vf, 'rb') as vf2: bot.send_video(uid, vf2, caption=f"✅ {i+1}/{len(urls)}", timeout=120)
                        s += 1
                    else: f += 1; update_user_balance(uid, cp)
                    for ff in os.listdir(tmpdir):
                        try: os.remove(os.path.join(tmpdir, ff))
                        except: pass
                except: f += 1; update_user_balance(uid, cp)
            bot.edit_message_text(f"✅ Bulk Download Complete!\n\n✅ Success: {s}\n❌ Failed: {f}", chat_id=message.chat.id, message_id=sm.message_id, reply_markup=back_button())
            log_usage(uid, "instagram_bulk", f"Bulk: {s} success, {f} failed")
            shutil.rmtree(tmpdir, ignore_errors=True)
        except Exception as e:
            shutil.rmtree(tmpdir, ignore_errors=True)
            bot.edit_message_text(f"❌ Error: {str(e)[:200]}", chat_id=message.chat.id, message_id=sm.message_id, reply_markup=back_button())
    threading.Thread(target=thread).start()

# ==================== IG VIEWER HANDLER ====================
@bot.message_handler(func=lambda m: user_igviewer_state.get(m.from_user.id) == "waiting_igviewer_username")
def igviewer_username_handler(message):
    uid = message.from_user.id; uname = message.text.strip()
    if uname.lower() in ['/cancel', 'cancel']:
        user_igviewer_state[uid] = None; bot.reply_to(message, "❌ IG Viewer cancelled.", reply_markup=back_button()); return
    if not uname or not re.match(r'^[a-zA-Z0-9_.]+$', uname):
        bot.reply_to(message, "❌ Invalid username.\n\nSend /cancel to abort."); return
    cost = get_module_cost("igviewer")
    if get_user_balance(uid) < cost:
        bot.reply_to(message, f"❌ Insufficient credits! Need {cost} credits. Balance: {get_user_balance(uid)}"); return
    update_user_balance(uid, -cost); user_igviewer_state[uid] = None
    sm = bot.reply_to(message, f"🔍 Fetching @{uname}...")
    def thread():
        try:
            data, err = fetch_ig_profile(uname)
            if err:
                update_user_balance(uid, cost)
                bot.edit_message_text(f"❌ Error: {err}", chat_id=message.chat.id, message_id=sm.message_id, reply_markup=back_button()); return
            log_usage(uid, "igviewer", f"Viewed {uname}")
            prof = data.get("profile", {}) or data.get("user", {}) or data or {}
            fn = prof.get("full_name", prof.get("fullName", "N/A"))
            bio = prof.get("biography", prof.get("bio", "N/A"))
            followers = prof.get("follower_count", prof.get("followers", prof.get("followerCount", 0)))
            following = prof.get("following_count", prof.get("following", prof.get("followingCount", 0)))
            posts = prof.get("media_count", prof.get("posts", prof.get("mediaCount", 0)))
            pvt = prof.get("is_private", prof.get("isPrivate", False))
            ver = prof.get("is_verified", prof.get("isVerified", False))
            pic = prof.get("profile_pic_url", prof.get("profilePicUrl", prof.get("avatar", "")))
            r = f"👤 @{uname} {'✅ Verified' if ver else ''}\n📛 {fn}\n{'🔒 Private' if pvt else '🌍 Public'}\n━━━━━━━━━━━━\n📸 Posts: {posts}\n👥 Followers: {followers}\n👣 Following: {following}\n━━━━━━━━━━━━\n📝 {bio[:200]}" if bio != "N/A" else ""
            if pic:
                try:
                    bot.send_photo(uid, pic, caption=r, reply_markup=back_button())
                    bot.delete_message(chat_id=message.chat.id, message_id=sm.message_id); return
                except: pass
            bot.edit_message_text(r, chat_id=message.chat.id, message_id=sm.message_id, reply_markup=back_button())
        except Exception as e:
            update_user_balance(uid, cost)
            bot.edit_message_text(f"❌ Error: {str(e)[:200]}", chat_id=message.chat.id, message_id=sm.message_id, reply_markup=back_button())
    threading.Thread(target=thread).start()

# ==================== MUSIC SEARCH HANDLER ====================
@bot.message_handler(func=lambda m: user_music_state.get(m.from_user.id) == "waiting_music_query")
def music_search_handler(message):
    uid = message.from_user.id; query = message.text.strip()
    if query.lower() in ['/cancel', 'cancel']:
        user_music_state[uid] = None; bot.reply_to(message, "❌ Music search cancelled.", reply_markup=back_button()); return
    if not query:
        bot.reply_to(message, "❌ Please enter a search query.\n\nSend /cancel to abort."); return
    sm = bot.reply_to(message, f"🎵 Searching for \"{query}\"...")
    def thread():
        try:
            results, err = search_music_youtube(query)
            if err:
                bot.edit_message_text(f"❌ Search failed: {err}", chat_id=message.chat.id, message_id=sm.message_id, reply_markup=back_button())
                user_music_state[uid] = None; return
            if not results:
                bot.edit_message_text("❌ No results found.", chat_id=message.chat.id, message_id=sm.message_id, reply_markup=back_button())
                user_music_state[uid] = None; return
            user_music_state[uid] = "waiting_music_select"
            user_temp_sessions[uid] = {"results": results}
            text = f"🎵 Results for \"{query}\"\n\n"
            kb = InlineKeyboardMarkup()
            for i, r in enumerate(results[:5]):
                d = r.get('duration', 0); m = d//60; s = d%60
                text += f"{i+1}. {r['title'][:50]}\n   👤 {r['uploader']} | ⏱️ {m}:{s:02d}\n\n"
                kb.row(InlineKeyboardButton(f"🎵 {i+1}. {r['title'][:30]}...", callback_data=f"music_dl_{i}"))
            kb.row(InlineKeyboardButton("🔍 New Search", callback_data="music_search"))
            kb.row(InlineKeyboardButton("🔙 Back", callback_data="back_menu"))
            bot.edit_message_text(text, chat_id=message.chat.id, message_id=sm.message_id, reply_markup=kb)
        except Exception as e:
            bot.edit_message_text(f"❌ Error: {str(e)[:200]}", chat_id=message.chat.id, message_id=sm.message_id, reply_markup=back_button())
            user_music_state[uid] = None
    threading.Thread(target=thread).start()

# ==================== FIREBASE APK HANDLER ====================
@bot.message_handler(content_types=['document'])
def firebase_apk_handler(message):
    uid = message.from_user.id
    if user_firebase_state.get(uid) != "waiting_apk": return
    doc = message.document
    if not doc.file_name.endswith('.apk'):
        bot.reply_to(message, "❌ Please send an APK file.", reply_markup=back_button()); return
    if doc.file_size > 50 * 1024 * 1024:
        update_user_balance(uid, get_module_cost("firebase"))
        bot.reply_to(message, "❌ File too large! Max 50 MB.", reply_markup=back_button())
        user_firebase_state[uid] = None; return
    cost = get_module_cost("firebase")
    if get_user_balance(uid) < cost:
        bot.reply_to(message, f"❌ Insufficient credits! Need {cost}. Balance: {get_user_balance(uid)}"); return
    update_user_balance(uid, -cost); user_firebase_state[uid] = None
    sm = bot.reply_to(message, "⬇️ Downloading APK..."); tmpdir = tempfile.mkdtemp()
    def thread():
        try:
            fi = bot.get_file(doc.file_id); dl = bot.download_file(fi.file_path)
            ap = os.path.join(tmpdir, doc.file_name)
            with open(ap, 'wb') as f: f.write(dl)
            bot.edit_message_text("🔍 Extracting credentials...", chat_id=message.chat.id, message_id=sm.message_id)
            res = scan_apk_for_firebase(ap)
            txt = f"✅ APK Analysis Complete\n\n📁 {doc.file_name}\n━━━━━━━━━━━━\n\n"
            has = False
            if res["firebase_urls"]:
                has = True; txt += f"🔥 Firebase URLs ({len(res['firebase_urls'])}):\n"
                for u in res["firebase_urls"][:10]: txt += f"  {u}\n"
                if len(res["firebase_urls"]) > 10: txt += f"  ... +{len(res['firebase_urls'])-10} more\n"
                txt += "\n"
            if res["api_keys"]:
                has = True; txt += f"🔑 API Keys ({len(res['api_keys'])}):\n"
                for k in res["api_keys"][:10]: txt += f"  {k}\n"
                if len(res["api_keys"]) > 10: txt += f"  ... +{len(res['api_keys'])-10} more\n"
                txt += "\n"
            if res["storage_buckets"]:
                has = True; txt += f"📦 Storage ({len(res['storage_buckets'])}):\n"
                for b in res["storage_buckets"][:10]: txt += f"  {b}\n"
                if len(res["storage_buckets"]) > 10: txt += f"  ... +{len(res['storage_buckets'])-10} more\n"
                txt += "\n"
            if res["secrets"]:
                has = True; txt += f"🔐 Secrets ({len(res['secrets'])}):\n"
                for s in res["secrets"][:10]: txt += f"  {s[:50]}\n"
                if len(res["secrets"]) > 10: txt += f"  ... +{len(res['secrets'])-10} more\n"
                txt += "\n"
            if res["json_endpoints"]:
                has = True; txt += f"📄 JSON ({len(res['json_endpoints'])}):\n"
                for e in res["json_endpoints"][:10]: txt += f"  {e}\n"
                if len(res["json_endpoints"]) > 10: txt += f"  ... +{len(res['json_endpoints'])-10} more\n"
            if not has: txt += "⚠️ No Firebase credentials found."
            log_usage(uid, "firebase", f"Analyzed {doc.file_name}: {len(res['firebase_urls'])} URLs, {len(res['api_keys'])} keys")
            bot.edit_message_text(txt, chat_id=message.chat.id, message_id=sm.message_id, reply_markup=back_button())
            shutil.rmtree(tmpdir, ignore_errors=True)
        except Exception as e:
            shutil.rmtree(tmpdir, ignore_errors=True); update_user_balance(uid, cost)
            bot.edit_message_text(f"❌ Analysis failed: {str(e)[:200]}", chat_id=message.chat.id, message_id=sm.message_id, reply_markup=back_button())
    threading.Thread(target=thread).start()

# ==================== CALLBACK QUERY HANDLER ====================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    uid = call.from_user.id; data = call.data

    if data == "back_menu":
        user = get_user(uid)
        if not user: bot.answer_callback_query(call.id, "User not found"); return
        for d in [user_firebase_state, user_instagram_state, user_music_state, user_shopsy_state, user_yoga_state, user_igviewer_state, user_flipkart_state, user_supercoin_state]:
            d[uid] = None
        for d in [user_shopsy_otp_data, user_yoga_otp_data, user_supercoin_otp_data]:
            if uid in d: del d[uid]
        bot.edit_message_text(main_menu_text(uid, user['first_name'], user['balance'], "✅" if check_membership(uid) else "❌"),
            chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=main_menu_keyboard(uid == ADMIN_ID))
        bot.answer_callback_query(call.id); return

    if data == "back_shopsy":
        user = get_user(uid); user_shopsy_state[uid] = None
        if uid in user_shopsy_otp_data: del user_shopsy_otp_data[uid]
        bot.edit_message_text(shopsy_menu_text(uid, user['balance'], "✅", get_shopsy_balance(uid), get_shopsy_login_status(uid)),
            chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=shopsy_menu_keyboard())
        bot.answer_callback_query(call.id); return

    if data == "back_yoga":
        user = get_user(uid); user_yoga_state[uid] = None
        if uid in user_yoga_otp_data: del user_yoga_otp_data[uid]
        bot.edit_message_text(yoga_menu_text(uid, user['balance'], "✅", user.get('yoga_code'), get_yoga_refer_reward(), get_module_cost("yoga")),
            chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=yoga_menu_keyboard())
        bot.answer_callback_query(call.id); return

    if data.startswith("module_"):
        module = data.replace("module_", ""); user = get_user(uid)
        if not user: bot.answer_callback_query(call.id, "User not found"); return
        bal = user['balance']; st = "✅" if check_membership(uid) else "❌"
        texts = {
            "firebase": (firebase_menu_text(uid, bal, st, get_module_cost("firebase")), firebase_menu_keyboard()),
            "temp": (temp_menu_text(uid), temp_menu_keyboard()),
            "flipkart": (flipkart_menu_text(uid, bal, st, get_module_cost("flipkart")), flipkart_menu_keyboard()),
            "instagram": (instagram_menu_text(uid, bal, st, get_module_cost("instagram_single")), instagram_menu_keyboard()),
            "igviewer": (igviewer_menu_text(uid, bal, st, get_module_cost("igviewer")), igviewer_menu_keyboard()),
            "music": (music_menu_text(uid), music_menu_keyboard()),
            "shopsy": (shopsy_menu_text(uid, bal, st, get_shopsy_balance(uid), get_shopsy_login_status(uid)), shopsy_menu_keyboard()),
            "yoga": (yoga_menu_text(uid, bal, st, user.get('yoga_code'), get_yoga_refer_reward(), get_module_cost("yoga")), yoga_menu_keyboard()),
            "supercoin": (supercoin_menu_text(uid, bal, st, get_module_cost("supercoin")), supercoin_menu_keyboard()),
            "referral": (referral_menu_text(uid, bal, get_referral_count(uid), get_pending_referral_count(uid)), referral_menu_keyboard()),
            "admin": (admin_panel_text(), admin_panel_keyboard()),
        }
        if module in texts:
            txt, kb = texts[module]
            if module == "admin" and uid != ADMIN_ID:
                bot.answer_callback_query(call.id, "Unauthorized"); return
            bot.edit_message_text(txt, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=kb)
        elif module == "stats":
            bot.answer_callback_query(call.id, f"📊 Users: {get_total_users()} | Coins: {get_total_coins()} | Usage: {get_total_usage()}", show_alert=True)
        else: bot.answer_callback_query(call.id, "Module not found")
        bot.answer_callback_query(call.id); return

    # FIREBASE
    if data == "firebase_send":
        user_firebase_state[uid] = "waiting_apk"
        bot.edit_message_text("📤 Send APK File\n\nUpload your .apk file now.\nMax 50 MB.\n\nSend /cancel to abort.",
            chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=back_button())
        bot.answer_callback_query(call.id); return
    if data == "firebase_remove":
        user_firebase_state[uid] = None
        bot.edit_message_text("❌ Firebase analysis cancelled.", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=back_button())
        bot.answer_callback_query(call.id); return

    # TEMP MAIL
    if data == "temp_new":
        sm = bot.edit_message_text("📧 Generating new email...", chat_id=call.message.chat.id, message_id=call.message.message_id)
        def t():
            try:
                r, e = create_temp_email()
                if e: bot.edit_message_text(f"❌ Failed: {e}", chat_id=call.message.chat.id, message_id=sm.message_id, reply_markup=back_button()); return
                conn = sqlite3.connect(DB_PATH, check_same_thread=False)
                c = conn.cursor(); c.execute('DELETE FROM temp_emails WHERE user_id = ?', (uid,))
                c.execute('INSERT INTO temp_emails (user_id, email, password, token) VALUES (?, ?, ?, ?)', (uid, r['email'], r['password'], r['token']))
                conn.commit(); conn.close()
                bot.edit_message_text(f"✅ Email Created!\n\n📧 {r['email']}\n🔑 {r['password']}\n⏱️ Valid for 10 minutes",
                    chat_id=call.message.chat.id, message_id=sm.message_id, reply_markup=temp_menu_keyboard())
            except Exception as ex: bot.edit_message_text(f"❌ Error: {str(ex)[:200]}", chat_id=call.message.chat.id, message_id=sm.message_id, reply_markup=back_button())
        threading.Thread(target=t).start(); bot.answer_callback_query(call.id); return

    if data == "temp_inbox":
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor(); c.execute('SELECT email, token FROM temp_emails WHERE user_id = ? ORDER BY created_at DESC LIMIT 1', (uid,))
        row = c.fetchone(); conn.close()
        if not row: bot.answer_callback_query(call.id, "❌ No active email!", show_alert=True); return
        email, token = row
        sm = bot.edit_message_text(f"📥 Checking inbox for {email}...", chat_id=call.message.chat.id, message_id=call.message.message_id)
        def t():
            try:
                msgs, e = get_temp_mail_messages(token)
                if e: bot.edit_message_text(f"❌ {e}", chat_id=call.message.chat.id, message_id=sm.message_id, reply_markup=back_button()); return
                if not msgs: bot.edit_message_text(f"📥 Inbox empty\n\n📧 {email}\n\nNo messages yet.", chat_id=call.message.chat.id, message_id=sm.message_id, reply_markup=temp_menu_keyboard()); return
                txt = f"📥 Inbox ({len(msgs)} messages)\n\n📧 {email}\n\n"
                for i, m in enumerate(msgs[:5]):
                    txt += f"{i+1}. {m.get('subject','No subject')[:40]}\n   📩 {m.get('from',{}).get('address','Unknown')}\n   🕐 {str(m.get('createdAt',''))[:19]}\n\n"
                bot.edit_message_text(txt, chat_id=call.message.chat.id, message_id=sm.message_id, reply_markup=temp_menu_keyboard())
            except Exception as ex: bot.edit_message_text(f"❌ Error: {str(ex)[:200]}", chat_id=call.message.chat.id, message_id=sm.message_id, reply_markup=back_button())
        threading.Thread(target=t).start(); bot.answer_callback_query(call.id); return

    if data == "temp_otp":
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor(); c.execute('SELECT email, token FROM temp_emails WHERE user_id = ? ORDER BY created_at DESC LIMIT 1', (uid,))
        row = c.fetchone(); conn.close()
        if not row: bot.answer_callback_query(call.id, "❌ No active email!", show_alert=True); return
        email, token = row
        sm = bot.edit_message_text(f"🔍 Scanning for OTP in {email}...", chat_id=call.message.chat.id, message_id=call.message.message_id)
        def t():
            try:
                msgs, e = get_temp_mail_messages(token)
                if e or not msgs: bot.edit_message_text("❌ No messages found.", chat_id=call.message.chat.id, message_id=sm.message_id, reply_markup=temp_menu_keyboard()); return
                found = None
                for m in msgs:
                    mid = m.get('id')
                    if mid:
                        md, _ = get_temp_message_content(token, mid)
                        if md:
                            otp = extract_otp_from_message(md)
                            if otp: found = otp; break
                if found: bot.edit_message_text(f"✅ OTP Found!\n\n🔑 Code: {found}\n📧 {email}", chat_id=call.message.chat.id, message_id=sm.message_id, reply_markup=temp_menu_keyboard())
                else: bot.edit_message_text("❌ No OTP found in your emails.", chat_id=call.message.chat.id, message_id=sm.message_id, reply_markup=temp_menu_keyboard())
            except Exception as ex: bot.edit_message_text(f"❌ Error: {str(ex)[:200]}", chat_id=call.message.chat.id, message_id=sm.message_id, reply_markup=back_button())
        threading.Thread(target=t).start(); bot.answer_callback_query(call.id); return

    if data == "temp_delete":
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor(); c.execute('SELECT token FROM temp_emails WHERE user_id = ? ORDER BY created_at DESC LIMIT 1', (uid,))
        row = c.fetchone()
        if row: delete_temp_email(row[0])
        c.execute('DELETE FROM temp_emails WHERE user_id = ?', (uid,))
        conn.commit(); conn.close()
        bot.edit_message_text("🗑️ Email deleted!", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=temp_menu_keyboard())
        bot.answer_callback_query(call.id); return

    # FLIPKART
    if data == "flipkart_check":
        user_flipkart_state[uid] = "waiting_flipkart_number"
        ab = InlineKeyboardMarkup(); ab.row(InlineKeyboardButton("❌ Abort", callback_data="flipkart_abort")); ab.row(InlineKeyboardButton("🔙 Back", callback_data="back_menu"))
        bot.edit_message_text("📱 Check Flipkart Registration\n\nEnter 10-digit phone number:\n\nSend /cancel to abort.",
            chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=ab)
        bot.answer_callback_query(call.id); return
    if data == "flipkart_abort":
        user_flipkart_state[uid] = None
        bot.edit_message_text("❌ Flipkart check cancelled.", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=back_button())
        bot.answer_callback_query(call.id); return

    # INSTAGRAM
    if data == "instagram_single":
        if get_user_balance(uid) < get_module_cost("instagram_single"):
            bot.answer_callback_query(call.id, "❌ Insufficient credits!", show_alert=True); return
        user_instagram_state[uid] = "waiting_instagram_single"
        ab = InlineKeyboardMarkup(); ab.row(InlineKeyboardButton("❌ Abort", callback_data="instagram_abort")); ab.row(InlineKeyboardButton("🔙 Back", callback_data="back_menu"))
        bot.edit_message_text("📹 Single Reel Download\n\nSend the Instagram reel URL:\n\nExample: https://www.instagram.com/reel/xyz/\n\nSend /cancel to abort.",
            chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=ab)
        bot.answer_callback_query(call.id); return
    if data == "instagram_bulk":
        if get_user_balance(uid) < get_module_cost("instagram_bulk"):
            bot.answer_callback_query(call.id, "❌ Insufficient credits!", show_alert=True); return
        user_instagram_state[uid] = "waiting_instagram_bulk"
        ab = InlineKeyboardMarkup(); ab.row(InlineKeyboardButton("❌ Abort", callback_data="instagram_abort")); ab.row(InlineKeyboardButton("🔙 Back", callback_data="back_menu"))
        bot.edit_message_text("📚 Bulk Download\n\nSend URLs (one per line):\n\nhttps://www.instagram.com/reel/abc/\nhttps://www.instagram.com/reel/xyz/\n\nSend /cancel to abort.",
            chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=ab)
        bot.answer_callback_query(call.id); return    if data == "instagram_abort":
        user_instagram_state[uid] = None
        bot.edit_message_text("❌ Instagram download cancelled.", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=back_button())
        bot.answer_callback_query(call.id); return

    # IG VIEWER
    if data == "igviewer_view":
        if get_user_balance(uid) < get_module_cost("igviewer"):
            bot.answer_callback_query(call.id, "❌ Insufficient credits!", show_alert=True); return
        user_igviewer_state[uid] = "waiting_igviewer_username"
        ab = InlineKeyboardMarkup(); ab.row(InlineKeyboardButton("❌ Abort", callback_data="igviewer_abort")); ab.row(InlineKeyboardButton("🔙 Back", callback_data="back_menu"))
        bot.edit_message_text("👤 View Instagram Profile\n\nEnter username (without @):\n\nExample: instagram\n\nSend /cancel to abort.",
            chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=ab)
        bot.answer_callback_query(call.id); return
    if data == "igviewer_abort":
        user_igviewer_state[uid] = None
        bot.edit_message_text("❌ IG Viewer cancelled.", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=back_button())
        bot.answer_callback_query(call.id); return

    # MUSIC
    if data == "music_search":
        user_music_state[uid] = "waiting_music_query"
        ab = InlineKeyboardMarkup(); ab.row(InlineKeyboardButton("❌ Abort", callback_data="music_abort")); ab.row(InlineKeyboardButton("🔙 Back", callback_data="back_menu"))
        bot.edit_message_text("🎵 Search Song\n\nEnter song name or artist:\n\nExample: Shape of You\n\nSend /cancel to abort.",
            chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=ab)
        bot.answer_callback_query(call.id); return
    if data == "music_abort":
        user_music_state[uid] = None
        bot.edit_message_text("❌ Music search cancelled.", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=back_button())
        bot.answer_callback_query(call.id); return
    if data.startswith("music_dl_"):
        idx = int(data.replace("music_dl_", "")); sess = user_temp_sessions.get(uid, {}); results = sess.get("results", [])
        if idx < 0 or idx >= len(results): bot.answer_callback_query(call.id, "❌ Invalid", show_alert=True); return
        song = results[idx]; title = song['title']; url = song['url']
        user_music_state[uid] = None
        sm = bot.edit_message_text(f"⬇️ Downloading {title[:50]}...", chat_id=call.message.chat.id, message_id=call.message.message_id)
        tmpdir = tempfile.mkdtemp()
        def t():
            try:
                fp, e = download_youtube_audio(url, tmpdir)
                if e:
                    shutil.rmtree(tmpdir, ignore_errors=True)
                    bot.edit_message_text(f"❌ Download failed: {e}", chat_id=call.message.chat.id, message_id=sm.message_id, reply_markup=back_button()); return
                if fp and os.path.exists(fp) and os.path.getsize(fp) < 50*1024*1024:
                    dur = song.get('duration',0); mins = dur//60; secs = dur%60
                    cap = f"🎵 {title}\n👤 {song['uploader']}\n⏱️ {mins}:{secs:02d}\n✅ @{bot.get_me().username}"
                    with open(fp, 'rb') as f: bot.send_audio(uid, f, caption=cap, title=title, performer=song['uploader'], timeout=120)
                    bot.delete_message(chat_id=call.message.chat.id, message_id=sm.message_id)
                    bot.send_message(uid, "✅ Download complete!", reply_markup=back_button())
                    log_usage(uid, "music", f"Downloaded {title}")
                else: bot.edit_message_text("❌ Download failed.", chat_id=call.message.chat.id, message_id=sm.message_id, reply_markup=back_button())
                shutil.rmtree(tmpdir, ignore_errors=True)
            except Exception as ex:
                shutil.rmtree(tmpdir, ignore_errors=True)
                bot.edit_message_text(f"❌ Error: {str(ex)[:200]}", chat_id=call.message.chat.id, message_id=sm.message_id, reply_markup=back_button())
        threading.Thread(target=t).start(); bot.answer_callback_query(call.id); return

    # SHOPSY
    if data == "shopsy_start":
        if get_shopsy_login_status(uid):
            phone, sd = get_shopsy_session(uid)
            if not sd:
                set_shopsy_login_status(uid, 0)
                bot.edit_message_text("Session expired. Login again.", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=back_button())
                bot.answer_callback_query(call.id); return
            cost = get_module_cost("shopsy")
            if get_user_balance(uid) < cost:
                bot.answer_callback_query(call.id, f"❌ Insufficient credits! Need {cost}", show_alert=True); return
            update_user_balance(uid, -cost)
            bot.edit_message_text("🚀 Starting mining...", chat_id=call.message.chat.id, message_id=call.message.message_id)
            async def prog(msg):
                try: bot.edit_message_text(msg, chat_id=call.message.chat.id, message_id=call.message.message_id)
                except: pass
            def t():
                try:
                    loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(core_mine_logic(sd, prog)); loop.close()
                    if result.get("status") == "success":
                        earned = result.get("earned",0); played = result.get("played",0); gems = result.get("gems",0)
                        update_shopsy_balance(uid, earned)
                        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
                        c = conn.cursor()
                        c.execute('INSERT INTO shopsy_mining_history (user_id, phone, coins_earned, games_played, gems_earned, time_taken) VALUES (?,?,?,?,?,?)',
                            (uid, phone, earned, played, gems, result.get("time_taken",0)))
                        conn.commit(); conn.close()
                        bot.edit_message_text(f"✅ Mining Complete!\n\n🪙 Coins: {earned}\n💎 Gems: {gems}\n🎮 Games: {played}/{result.get('total',0)}\n⏱️ {result.get('time_taken',0)}s\n📱 +91{phone}\n\n💰 Refunded: +{cost}",
                            chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=back_button())
                        update_user_balance(uid, cost)
                    else:
                        update_user_balance(uid, cost)
                        bot.edit_message_text(f"❌ Mining failed: {result.get('msg','Unknown')}", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=back_button())
                except Exception as e:
                    update_user_balance(uid, cost)
                    bot.edit_message_text(f"❌ Error: {str(e)[:200]}", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=back_button())
            threading.Thread(target=t).start()
        else:
            user_shopsy_state[uid] = "waiting_phone"
            kb = InlineKeyboardMarkup(); kb.row(InlineKeyboardButton("❌ Cancel", callback_data="shopsy_abort")); kb.row(InlineKeyboardButton("🔙 Back", callback_data="back_shopsy"))
            bot.edit_message_text("📱 Enter 10-digit phone number:\n\nSend /cancel to abort.",
                chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=kb)
        bot.answer_callback_query(call.id); return

    if data in ("shopsy_abort", "shopsy_abort_otp"):
        user_shopsy_state[uid] = None
        if uid in user_shopsy_otp_data: update_user_balance(uid, user_shopsy_otp_data[uid]["cost"]); del user_shopsy_otp_data[uid]
        bot.edit_message_text("❌ Shopsy cancelled.", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=back_button())
        bot.answer_callback_query(call.id); return

    if data == "shopsy_stats":
        phone, _ = get_shopsy_session(uid)
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor(); c.execute('SELECT COUNT(*), COALESCE(SUM(coins_earned),0), COALESCE(SUM(gems_earned),0), COALESCE(SUM(games_played),0) FROM shopsy_mining_history WHERE user_id = ?', (uid,))
        row = c.fetchone(); conn.close()
        txt = f"🛍️ Stats:\n📱 Phone: +91{phone if phone else 'N/A'}\n🪙 Balance: {get_shopsy_balance(uid)}\n🎮 Sessions: {row[0]}\n💎 Gems: {row[2]}\n🕹️ Games: {row[3]}" if row else f"🛍️ Stats:\n📱 Phone: +91{phone if phone else 'N/A'}\n🪙 Balance: {get_shopsy_balance(uid)}"
        bot.answer_callback_query(call.id, txt, show_alert=True); return

    if data == "shopsy_logout":
        logout_shopsy_user(uid)
        bot.edit_message_text("🚪 Logged out from Shopsy.", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=back_button())
        bot.answer_callback_query(call.id); return

    # SUPERCOIN
    if data == "supercoin_start":
        if get_user_balance(uid) < get_module_cost("supercoin"):
            bot.answer_callback_query(call.id, "❌ Insufficient credits!", show_alert=True); return
        user_supercoin_state[uid] = "waiting_supercoin_phone"
        ab = InlineKeyboardMarkup(); ab.row(InlineKeyboardButton("❌ Abort", callback_data="supercoin_abort")); ab.row(InlineKeyboardButton("🔙 Back", callback_data="back_menu"))
        bot.edit_message_text("📱 Fetch Supercoin Balance\n\nEnter 10-digit phone number:\n\nSend /cancel to abort.",
            chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=ab)
        bot.answer_callback_query(call.id); return
    if data in ("supercoin_abort", "supercoin_abort_otp"):
        user_supercoin_state[uid] = None
        if uid in user_supercoin_otp_data: update_user_balance(uid, user_supercoin_otp_data[uid]["cost"]); del user_supercoin_otp_data[uid]
        bot.edit_message_text("❌ Supercoin cancelled.", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=back_button())
        bot.answer_callback_query(call.id); return

    # YOGA
    if data == "yoga_start":
        user_yoga_state[uid] = "waiting_yoga_phone"
        kb = InlineKeyboardMarkup(); kb.row(InlineKeyboardButton("❌ Cancel", callback_data="yoga_abort")); kb.row(InlineKeyboardButton("🔙 Back", callback_data="back_yoga"))
        bot.edit_message_text("📱 Enter 10-digit phone number for Yoga:\n\nSend /cancel to abort.",
            chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=kb)
        bot.answer_callback_query(call.id); return
    if data in ("yoga_abort", "yoga_abort_otp"):
        user_yoga_state[uid] = None
        if uid in user_yoga_otp_data: update_user_balance(uid, user_yoga_otp_data[uid]["cost"]); del user_yoga_otp_data[uid]
        bot.edit_message_text("❌ Yoga cancelled.", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=back_button())
        bot.answer_callback_query(call.id); return
    if data == "yoga_setcode":
        bot.send_message(uid, "🔑 Set Yoga Referral Code\n\nSend your Habit.Yoga link or code:\n\nhttps://habit.yoga/ABC123\nABC123\n\nSend /cancel to abort.")
        user_yoga_state[uid] = "waiting_yoga_code"
        bot.answer_callback_query(call.id); return
    if data == "yoga_stats":
        user = get_user(uid)
        if user: bot.answer_callback_query(call.id, f"🧘 Yoga:\nCode: {user.get('yoga_code','Not set')}\nRefers: {user.get('yoga_bot_refers',0)}", show_alert=True)
        bot.answer_callback_query(call.id); return

    # REFERRAL
    if data == "referral_get_link":
        link = get_referral_link(uid)
        kb = InlineKeyboardMarkup(); kb.row(InlineKeyboardButton("📤 Share Link", callback_data="referral_share")); kb.row(InlineKeyboardButton("🔙 Back", callback_data="back_menu"))
        bot.edit_message_text(f"🔗 Your Referral Link\n\n{link}\n\n👥 Successful: {get_referral_count(uid)}\n⏳ Pending: {get_pending_referral_count(uid)}\n💰 Bonus: +{REFERRAL_BONUS} Credits per referral\n\nEach friend gets +{NEW_USER_BONUS} Credits!",
            chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=kb)
        bot.answer_callback_query(call.id); return
    if data == "referral_share":
        bot.answer_callback_query(call.id, "📤 Share this link:\n\n" + get_referral_link(uid), show_alert=True); return
    if data == "referral_stats":
        bot.answer_callback_query(call.id, f"📊 Referrals:\n✅ Completed: {get_referral_count(uid)}\n⏳ Pending: {get_pending_referral_count(uid)}\n💰 Balance: {get_user_balance(uid)}\n🎁 Bonus: +{REFERRAL_BONUS}/referral", show_alert=True); return

    # ADMIN
    if data.startswith("admin_"):
        if uid != ADMIN_ID: bot.answer_callback_query(call.id, "❌ Unauthorized!"); return
        a = data.replace("admin_", "")
        if a == "stats":
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            c = conn.cursor(); c.execute("SELECT COUNT(*) FROM users WHERE last_used >= datetime('now', '-7 days')")
            au = c.fetchone()[0]; conn.close()
            bot.answer_callback_query(call.id, f"📊 Stats:\n👥 Users: {get_total_users()}\n🟢 Active: {au}\n💰 Coins: {get_total_coins()}\n📈 Usage: {get_total_usage()}", show_alert=True); return
        if a == "users":
            users = get_all_users()
            if not users: bot.answer_callback_query(call.id, "No users", show_alert=True); return
            ul = "👥 Top Users:\n\n"
            for i, (uid2, un, bal, st) in enumerate(users[:10], 1):
                ul += f"{i}. {'🟢' if st=='ACTIVE' else '🔴'} {un or uid2} - 💰 {bal}\n"
            if len(users) > 10: ul += f"\n... +{len(users)-10} more"
            kb = InlineKeyboardMarkup(); kb.row(InlineKeyboardButton("📥 Export", callback_data="admin_export_users")); kb.row(InlineKeyboardButton("🔙 Back", callback_data="back_menu"))
            bot.edit_message_text(ul, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=kb)
            bot.answer_callback_query(call.id); return
        if a == "export_users":
            users = get_all_users()
            if not users: bot.answer_callback_query(call.id, "No users", show_alert=True); return
            csv = "User ID,Username,Balance,Status\n"
            for uid2, un, bal, st in users: csv += f"{uid2},{un or 'N/A'},{bal},{st}\n"
            try: bot.send_document(call.message.chat.id, document=("users.csv", csv), caption=f"📊 {len(users)} users"); bot.answer_callback_query(call.id, "✅ Exported!")
            except Exception as e: bot.answer_callback_query(call.id, f"❌ {str(e)[:50]}", show_alert=True); return
        if a == "add_coins":
            msg = bot.send_message(call.message.chat.id, "💰 Add Credits\n\nFormat: /addcoins USER_ID AMOUNT\n\nExample: /addcoins 123456789 10\n\nSend /cancel to abort.")
            bot.register_next_step_handler(msg, admin_add_coins_handler); bot.answer_callback_query(call.id); return
        if a == "remove_coins":
            msg = bot.send_message(call.message.chat.id, "➖ Remove Credits\n\nFormat: /removecoins USER_ID AMOUNT\n\nExample: /removecoins 123456789 5\n\nSend /cancel to abort.")
            bot.register_next_step_handler(msg, admin_remove_coins_handler); bot.answer_callback_query(call.id); return
        if a == "broadcast":
            msg = bot.send_message(call.message.chat.id, "📢 Broadcast\n\nSend the message to broadcast.\n\n⚠️ Sends to ALL users!\n\nSend /cancel to abort.")
            bot.register_next_step_handler(msg, admin_broadcast_handler); bot.answer_callback_query(call.id); return
        if a == "costs":
            ct = "⚙️ Module Costs\n\n"
            for mod, default in DEFAULT_COSTS.items(): ct += f"• {mod.title()}: {get_module_cost(mod)} credits\n"
            ct += f"\nUpdate: /setcost MODULE AMOUNT\nExample: /setcost yoga 2\n\n💰 Yoga Reward: {get_yoga_refer_reward()}"
            kb = InlineKeyboardMarkup(); kb.row(InlineKeyboardButton("🔙 Back", callback_data="back_menu"))
            bot.edit_message_text(ct, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=kb)
            bot.answer_callback_query(call.id); return

    if data == "broadcast_confirm":
        if uid != ADMIN_ID: bot.answer_callback_query(call.id, "❌ Unauthorized!"); return
        bm = getattr(bot, 'user_data', {}).get('broadcast_msg'); users = getattr(bot, 'user_data', {}).get('broadcast_users', [])
        if not bm: bot.answer_callback_query(call.id, "❌ No message!"); return
        bot.edit_message_text(f"📢 Broadcasting to {len(users)} users...", chat_id=call.message.chat.id, message_id=call.message.message_id)
        s = 0; f = 0
        for uid2, un, bal, st in users:
            try: bot.send_message(uid2, bm); s += 1; time.sleep(0.05)
            except: f += 1
        bot.edit_message_text(f"✅ Broadcast Complete!\n\n✅ Sent: {s}\n❌ Failed: {f}", chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.answer_callback_query(call.id, f"✅ Sent to {s} users"); return
    if data == "broadcast_cancel":
        if uid != ADMIN_ID: bot.answer_callback_query(call.id, "❌ Unauthorized!"); return
        bot.edit_message_text("❌ Broadcast cancelled.", chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.answer_callback_query(call.id); return

    bot.answer_callback_query(call.id)

# ==================== ADMIN HANDLERS ====================
def admin_add_coins_handler(message):
    uid = message.from_user.id
    if uid != ADMIN_ID: bot.reply_to(message, "❌ Unauthorized!"); return
    try:
        parts = message.text.strip().split()
        if len(parts) != 2: bot.reply_to(message, "❌ Use: /addcoins USER_ID AMOUNT"); return
        tid = int(parts[0]); amt = int(parts[1])
        if amt <= 0: bot.reply_to(message, "❌ Amount must be positive!"); return
        user = get_user(tid)
        if not user: bot.reply_to(message, f"❌ User {tid} not found!"); return
        update_user_balance(tid, amt)
        bot.reply_to(message, f"✅ Added {amt} Credits\n\n👤 {user['first_name']} (ID: {tid})\n💰 New Balance: {get_user_balance(tid)}")
        try: bot.send_message(tid, f"🎉 Admin added +{amt} Credits!\n💰 New Balance: {get_user_balance(tid)}")
        except: pass
    except: bot.reply_to(message, "❌ Invalid format!")

def admin_remove_coins_handler(message):
    uid = message.from_user.id
    if uid != ADMIN_ID: bot.reply_to(message, "❌ Unauthorized!"); return
    try:
        parts = message.text.strip().split()
        if len(parts) != 2: bot.reply_to(message, "❌ Use: /removecoins USER_ID AMOUNT"); return
        tid = int(parts[0]); amt = int(parts[1])
        if amt <= 0: bot.reply_to(message, "❌ Amount must be positive!"); return
        user = get_user(tid)
        if not user: bot.reply_to(message, f"❌ User {tid} not found!"); return
        if user['balance'] < amt: bot.reply_to(message, f"❌ Insufficient balance! Current: {user['balance']}"); return
        update_user_balance(tid, -amt)
        bot.reply_to(message, f"✅ Removed {amt} Credits\n\n👤 {user['first_name']} (ID: {tid})\n💰 New Balance: {get_user_balance(tid)}")
        try: bot.send_message(tid, f"⚠️ Admin removed -{amt} Credits.\n💰 New Balance: {get_user_balance(tid)}")
        except: pass
    except: bot.reply_to(message, "❌ Invalid format!")

def admin_broadcast_handler(message):
    uid = message.from_user.id
    if uid != ADMIN_ID: bot.reply_to(message, "❌ Unauthorized!"); return
    if message.text.lower() == '/cancel': bot.reply_to(message, "❌ Broadcast cancelled."); return
    users = get_all_users()
    if not users: bot.reply_to(message, "❌ No users!"); return
    kb = InlineKeyboardMarkup(); kb.row(InlineKeyboardButton("✅ Send", callback_data="broadcast_confirm"), InlineKeyboardButton("❌ Cancel", callback_data="broadcast_cancel"))
    if not hasattr(bot, 'user_data'): bot.user_data = {}
    bot.user_data['broadcast_msg'] = message.text; bot.user_data['broadcast_users'] = users
    bot.reply_to(message, f"📢 Broadcast Confirmation\n\n{message.text[:200]}\n\n👥 Recipients: {len(users)} users", reply_markup=kb)

# ==================== YOGA SET CODE HANDLER ====================
@bot.message_handler(func=lambda m: user_yoga_state.get(m.from_user.id) == "waiting_yoga_code")
def yoga_set_code_handler(message):
    uid = message.from_user.id; text = message.text.strip()
    if text.lower() in ['/cancel', 'cancel']:
        user_yoga_state[uid] = None; bot.reply_to(message, "❌ Yoga code setup cancelled.", reply_markup=back_button()); return
    code = extract_yoga_code(text)
    if not code:
        bot.reply_to(message, "❌ Invalid code.\n\nSend a valid Habit.Yoga link or code.\nExample: https://habit.yoga/ABC123"); return
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor(); c.execute('UPDATE users SET yoga_code = ? WHERE user_id = ?', (code, uid))
    conn.commit(); conn.close()
    user_yoga_state[uid] = None
    bot.reply_to(message, f"✅ Yoga Code Set!\n\n🔑 Code: {code}\n\nNow use Yoga Referral module!", reply_markup=back_button())

# ==================== SET COST COMMAND ====================
@bot.message_handler(commands=['setcost'])
def setcost_command(message):
    uid = message.from_user.id
    if uid != ADMIN_ID: bot.reply_to(message, "❌ Unauthorized!"); return
    try:
        parts = message.text.strip().split()
        if len(parts) != 3:
            bot.reply_to(message, "❌ Use: /setcost MODULE AMOUNT\n\nModules: firebase, flipkart, instagram_single, instagram_bulk, shopsy, yoga, igviewer, supercoin"); return
        module = parts[1].lower(); amt = int(parts[2])
        if amt < 0: bot.reply_to(message, "❌ Amount must be non-negative!"); return
        if module not in DEFAULT_COSTS: bot.reply_to(message, f"❌ Module '{module}' not found!\nAvailable: {', '.join(DEFAULT_COSTS.keys())}"); return
        set_config(f"{module}_cost", str(amt))
        bot.reply_to(message, f"✅ Cost Updated!\n\n📋 {module}\n💰 New Cost: {amt} credits")
    except: bot.reply_to(message, "❌ Amount must be a number!")

# ==================== START COMMAND ====================
@bot.message_handler(commands=['start'])
def start_command(message):
    uid = message.from_user.id; uname = message.from_user.username or ""; fname = message.from_user.first_name or "User"
    user = get_user(uid)
    ref_by = None
    if message.text and "ref_" in message.text:
        try: ref_by = int(message.text.split("ref_")[1].split()[0])
        except: pass
    if not user:
        create_user(uid, uname, fname, ref_by)
        user = get_user(uid)
        bot.send_message(uid, f"🎉 Welcome to Viediet Utility Bot!\n\n+{NEW_USER_BONUS} Credits as welcome bonus!\n\nExplore modules from the menu to get started!")
    status = "✅ Member" if check_membership(uid) else "❌ Not Joined"
    bot.send_message(uid, main_menu_text(uid, fname, get_user_balance(uid), status), reply_markup=main_menu_keyboard(uid == ADMIN_ID))

# ==================== MAIN ====================
if __name__ == "__main__":
    logger.info("🤖 Viediet Utility Bot starting...")
    logger.info("✅ All features enabled with proxy support")
    logger.info("🔄 Yoga, Shopsy, Flipkart using proxy rotation")
    logger.info("💰 Credit refund on failure enabled")
    logger.info("🔄 Abort and Back buttons for all features")
    try: bot.remove_webhook()
    except: pass
    while True:
        try:
            logger.info("🔄 Starting polling...")
            bot.polling(non_stop=True, interval=1, timeout=30)
        except Exception as e:
            logger.error(f"Polling error: {e}")
            logger.info("🔄 Restarting in 10 seconds...")
            time.sleep(10)
