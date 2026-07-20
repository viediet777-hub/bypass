#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# NRTECNO SYSTEM - VIEDIET BOT v2.0 FIXED
# All features included - Credit refund, Yoga fixes, Proxy support, Abort buttons

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
import concurrent.futures
import urllib.parse
import base64
import uuid
import itertools
from datetime import datetime, timedelta
from contextlib import suppress
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from curl_cffi import requests as cffi_requests

# ==================== PROXY CONFIGURATION ====================
# Load proxies from environment or use defaults
# Set these on Railway:
# PROXY_HOST=dc.decodo.com
# PROXY_USER=sptu9f11ur
# PROXY_PASS=0c_nm5z3eVm4jJEddL

class ProxyManager:
    """Centralized proxy management with environment variable support"""
    
    @staticmethod
    def get_proxy_config():
        """Get proxy config from environment or defaults"""
        return {
            "host": os.environ.get("PROXY_HOST", "dc.decodo.com"),
            "user": os.environ.get("PROXY_USER", "sptu9f11ur"),
            "pass": os.environ.get("PROXY_PASS", "0c_nm5z3eVm4jJEddL")
        }
    
    @staticmethod
    def get_yoga_proxies():
        config = ProxyManager.get_proxy_config()
        proxies = []
        for port in range(10001, 10011):
            proxies.append({
                "host": config["host"],
                "port": port,
                "user": config["user"],
                "pass": config["pass"]
            })
        return proxies
    
    @staticmethod
    def get_flipkart_proxies():
        config = ProxyManager.get_proxy_config()
        return [
            {"host": config["host"], "port": 10011, "user": config["user"], "pass": config["pass"]},
            {"host": config["host"], "port": 10012, "user": config["user"], "pass": config["pass"]},
        ]
    
    @staticmethod
    def get_shopsy_proxies():
        config = ProxyManager.get_proxy_config()
        return [
            {"host": config["host"], "port": 10013, "user": config["user"], "pass": config["pass"]},
            {"host": config["host"], "port": 10014, "user": config["user"], "pass": config["pass"]},
        ]

# Initialize proxies
PROXY_MANAGER = ProxyManager()
YOGA_PROXIES = PROXY_MANAGER.get_yoga_proxies()
FLIPKART_PROXIES = PROXY_MANAGER.get_flipkart_proxies()
SHOPSY_PROXIES = PROXY_MANAGER.get_shopsy_proxies()

_yoga_proxy_index = 0
_proxy_lock = threading.Lock()

def get_proxy_url(proxy):
    if not proxy:
        return None
    return f"http://{proxy['user']}:{proxy['pass']}@{proxy['host']}:{proxy['port']}"

def get_yoga_proxy():
    global _yoga_proxy_index
    if not YOGA_PROXIES:
        return None
    with _proxy_lock:
        proxy = YOGA_PROXIES[_yoga_proxy_index]
        _yoga_proxy_index = (_yoga_proxy_index + 1) % len(YOGA_PROXIES)
        return get_proxy_url(proxy)

def get_flipkart_proxy():
    if not FLIPKART_PROXIES:
        return None
    proxy = random.choice(FLIPKART_PROXIES)
    return get_proxy_url(proxy)

def get_shopsy_proxy():
    if not SHOPSY_PROXIES:
        return None
    proxy = random.choice(SHOPSY_PROXIES)
    return get_proxy_url(proxy)

# ==================== CONFIG ====================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    logging.error("BOT_TOKEN environment variable not set.")
    exit(1)

ADMIN_ID = int(os.environ.get("ADMIN_ID", 1364476174))
CHANNEL_USERNAME = "viedietlooters"
REFERRAL_BONUS = 3
NEW_USER_BONUS = 5
REFERRAL_STAY_HOURS = 1

YOGA_REFER_REWARD = 4
YOGA_WELCOME_BONUS = 2

DEFAULT_COSTS = {
    "firebase": 1,
    "flipkart": 1,
    "instagram_single": 1,
    "instagram_bulk": 1,
    "shopsy": 1,
    "yoga": 1,
}

# Yoga API endpoints
YOGA_REGISTER_URL = "https://auth-service.habuild.in/public/user/v1/register-user"
YOGA_LOGIN_URL = "https://auth-service.habuild.in/public/auth/v1/login"
YOGA_VERIFY_URL = "https://auth-service.habuild.in/public/auth/v1/verify-otp"

YOGA_HEADERS = {
    "accept": "application/json",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://habit.yoga",
    "referer": "https://habit.yoga/",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1",
}
YOGA_REG_HEADERS = {**YOGA_HEADERS, "authorization": "Bearer"}

YOGA_NAMES = [
    "Aarav","Vivaan","Aditya","Vihaan","Arjun","Sai","Shaurya","Atharva","Yash","Dhruv",
    "Kabir","Reyansh","Krishna","Laksh","Advik","Pranav","Rudra","Ishaan","Dev","Ansh",
    "Anaya","Aaradhya","Navya","Myra","Ananya","Diya","Sara","Ishita","Aadhya","Riya",
    "Raj","Simran","Priya","Rahul","Neha","Amit","Pooja","Vikram","Anjali","Rohan",
]

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

DB_PATH = "viediet_bot.db"
SHOPSY_SESSIONS_DIR = "shopsy_sessions"
os.makedirs(SHOPSY_SESSIONS_DIR, exist_ok=True)

# ==================== DATABASE ====================
def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        balance INTEGER DEFAULT 15,
        status TEXT DEFAULT 'ACTIVE',
        registered_at TEXT,
        last_used TEXT,
        referred_by INTEGER DEFAULT NULL,
        referral_code TEXT UNIQUE,
        account_age_days INTEGER DEFAULT 0,
        is_valid INTEGER DEFAULT 1,
        ip_address TEXT DEFAULT NULL,
        last_check TEXT DEFAULT NULL,
        shopsy_balance INTEGER DEFAULT 0,
        shopsy_is_logged_in INTEGER DEFAULT 0,
        yoga_code TEXT DEFAULT NULL,
        yoga_refers INTEGER DEFAULT 0,
        yoga_bot_refers INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS referrals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        referrer_id INTEGER,
        referred_id INTEGER UNIQUE,
        join_timestamp TEXT,
        leave_timestamp TEXT DEFAULT NULL,
        points_awarded INTEGER DEFAULT 0,
        is_valid INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS pending_referrals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        referrer_id INTEGER,
        referred_id INTEGER UNIQUE,
        join_timestamp TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS usage_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        module TEXT,
        details TEXT,
        timestamp TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS config (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS shopsy_sessions (
        user_id INTEGER PRIMARY KEY,
        phone TEXT,
        session_data TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS shopsy_mining_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        phone TEXT,
        coins_earned INTEGER,
        games_played INTEGER,
        gems_earned INTEGER,
        time_taken INTEGER,
        mined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()
    logger.info("Database initialized.")

init_db()

# ==================== CREDIT MANAGER (REFUND ON FAILURE) ====================
class CreditManager:
    """Handle credit deduction with automatic refund on failure"""
    
    def __init__(self, user_id, cost, operation_name=""):
        self.user_id = user_id
        self.cost = cost
        self.operation_name = operation_name
        self.deducted = False
        self.balance_before = 0
    
    def __enter__(self):
        return self
    
    def deduct(self):
        """Deduct credits from user"""
        self.balance_before = get_user_balance(self.user_id)
        if self.balance_before < self.cost:
            raise ValueError(f"Insufficient credits! Need {self.cost}")
        update_user_balance(self.user_id, -self.cost)
        self.deducted = True
        logger.info(f"💰 Deducted {self.cost} credits from user {self.user_id} for {self.operation_name}")
        return self
    
    def refund(self):
        """Refund credits to user"""
        if self.deducted:
            update_user_balance(self.user_id, self.cost)
            self.deducted = False
            logger.info(f"💰 Refunded {self.cost} credits to user {self.user_id} for {self.operation_name}")
            return True
        return False
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.refund()
            return False

# ==================== DATABASE FUNCTIONS ====================
def get_user(user_id):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            'user_id': row[0], 'username': row[1], 'first_name': row[2],
            'balance': row[3], 'status': row[4], 'registered_at': row[5],
            'last_used': row[6], 'referred_by': row[7], 'referral_code': row[8],
            'account_age_days': row[9], 'is_valid': row[10], 'ip_address': row[11],
            'last_check': row[12], 'shopsy_balance': row[13] if len(row) > 13 else 0,
            'shopsy_is_logged_in': row[14] if len(row) > 14 else 0,
            'yoga_code': row[15] if len(row) > 15 else None,
            'yoga_refers': row[16] if len(row) > 16 else 0,
            'yoga_bot_refers': row[17] if len(row) > 17 else 0
        }
    return None

def create_user(user_id, username, first_name, referred_by=None, ip_address=None):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    now = datetime.now().isoformat()
    ref_code = f"REF{user_id}{random.randint(1000, 9999)}"
    c.execute('''INSERT OR IGNORE INTO users 
        (user_id, username, first_name, balance, status, registered_at, last_used, referred_by, referral_code, ip_address, shopsy_balance, shopsy_is_logged_in, yoga_code, yoga_refers, yoga_bot_refers)
        VALUES (?, ?, ?, ?, 'ACTIVE', ?, ?, ?, ?, ?, 0, 0, ?, 0, 0)''',
        (user_id, username, first_name, NEW_USER_BONUS, now, now, referred_by, ref_code, ip_address, None))
    conn.commit()
    conn.close()
    if referred_by:
        add_pending_referral(referred_by, user_id)
    return NEW_USER_BONUS

def update_user_balance(user_id, delta):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (delta, user_id))
    conn.commit()
    conn.close()

def get_user_balance(user_id):
    user = get_user(user_id)
    return user['balance'] if user else 15

def get_shopsy_balance(user_id):
    user = get_user(user_id)
    return user['shopsy_balance'] if user else 0

def update_shopsy_balance(user_id, amount):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('UPDATE users SET shopsy_balance = shopsy_balance + ? WHERE user_id = ?', (amount, user_id))
    conn.commit()
    conn.close()

def get_shopsy_login_status(user_id):
    user = get_user(user_id)
    return user.get('shopsy_is_logged_in', 0) if user else 0

def set_shopsy_login_status(user_id, status):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('UPDATE users SET shopsy_is_logged_in = ? WHERE user_id = ?', (1 if status else 0, user_id))
    conn.commit()
    conn.close()

def get_referral_count(user_id):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM referrals WHERE referrer_id = ? AND is_valid = 1', (user_id,))
    count = c.fetchone()[0]
    conn.close()
    return count

def get_pending_referral_count(user_id):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM pending_referrals WHERE referrer_id = ?', (user_id,))
    count = c.fetchone()[0]
    conn.close()
    return count

def add_pending_referral(referrer_id, referred_id):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    now = datetime.now().isoformat()
    try:
        c.execute('INSERT INTO pending_referrals (referrer_id, referred_id, join_timestamp) VALUES (?, ?, ?)',
                  (referrer_id, referred_id, now))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

def check_and_award_referrals():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    now = datetime.now()
    c.execute('SELECT id, referrer_id, referred_id, join_timestamp FROM pending_referrals')
    pending = c.fetchall()
    for pid, referrer_id, referred_id, join_ts in pending:
        join_time = datetime.fromisoformat(join_ts)
        if (now - join_time) >= timedelta(hours=REFERRAL_STAY_HOURS):
            try:
                channel_member = bot.get_chat_member(f"@{CHANNEL_USERNAME}", referred_id)
                if channel_member.status in ['member', 'administrator', 'creator']:
                    update_user_balance(referrer_id, REFERRAL_BONUS)
                    c.execute('INSERT INTO referrals (referrer_id, referred_id, join_timestamp, points_awarded, is_valid) VALUES (?, ?, ?, ?, 1)',
                              (referrer_id, referred_id, join_ts, REFERRAL_BONUS))
                    c.execute('DELETE FROM pending_referrals WHERE id = ?', (pid,))
                    conn.commit()
                    try:
                        bot.send_message(referrer_id, f"🎉 <b>Referral Bonus!</b>\n\nYou earned <b>+{REFERRAL_BONUS} Credits</b> for referring a user who stayed in our community for 24 hours!\n💰 New balance: {get_user_balance(referrer_id)}", parse_mode="HTML")
                    except:
                        pass
            except Exception as e:
                logger.error(f"Referral award error for pending {pid}: {e}")
    conn.close()

def get_referral_link(user_id):
    bot_username = bot.get_me().username
    return f"https://t.me/{bot_username}?start=ref_{user_id}"

def log_usage(user_id, module, details=""):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute('INSERT INTO usage_logs (user_id, module, details, timestamp) VALUES (?, ?, ?, ?)',
              (user_id, module, details, now))
    c.execute('UPDATE users SET last_used = ? WHERE user_id = ?', (now, user_id))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT user_id, username, balance, status FROM users ORDER BY balance DESC')
    rows = c.fetchall()
    conn.close()
    return rows

def get_total_users():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM users')
    count = c.fetchone()[0]
    conn.close()
    return count

def get_total_coins():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT SUM(balance) FROM users')
    total = c.fetchone()[0]
    conn.close()
    return total if total else 0

def get_total_usage():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM usage_logs')
    count = c.fetchone()[0]
    conn.close()
    return count

def get_config(key, default=None):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT value FROM config WHERE key = ?', (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else default

def set_config(key, value):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('REPLACE INTO config (key, value) VALUES (?, ?)', (key, value))
    conn.commit()
    conn.close()

def get_module_cost(module):
    cost = get_config(f"{module}_cost")
    if cost:
        return int(cost)
    return DEFAULT_COSTS.get(module, 1)

def get_yoga_refer_reward():
    return get_config("yoga_refer_reward", YOGA_REFER_REWARD)

def get_yoga_welcome_bonus():
    return get_config("yoga_welcome_bonus", YOGA_WELCOME_BONUS)

# ==================== YOGA PROXY FUNCTIONS ====================
def yoga_api_post(url, payload, headers, use_proxy=True):
    try:
        proxy_url = get_yoga_proxy() if use_proxy else None
        proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None
        
        response = requests.post(
            url, 
            json=payload, 
            headers=headers, 
            timeout=30,
            proxies=proxies
        )
        
        if response.status_code in (200, 201):
            try:
                return response.json(), None
            except:
                return None, "Invalid JSON response"
        return None, f"HTTP {response.status_code}: {response.text[:150]}"
    except requests.exceptions.Timeout:
        return None, "Timeout"
    except requests.exceptions.ConnectionError:
        return None, "Connection Error"
    except Exception as e:
        return None, str(e)

def yoga_register(phone, code, name, did, sid):
    return yoga_api_post(YOGA_REGISTER_URL, {
        "name": name, "phoneNumber": phone, "referredBy": code,
        "sourceData": {"type": "Referral", "refererurl": "", "timezone": "Asia/Kolkata"},
        "experimentMetaInfo": {"deviceId": did, "sessionId": sid},
    }, YOGA_REG_HEADERS)

def yoga_send_otp(phone, did, sid):
    resp, err = yoga_api_post(YOGA_LOGIN_URL, {
        "method": "phone_otp", "otpChannel": "sms", "phoneNumber": phone,
        "sourceData": {"type": "portal", "utm_source": "web_app"},
        "experimentMetaInfo": {"deviceId": did, "sessionId": sid},
        "registerUser": False,
    }, YOGA_HEADERS)
    if err:
        return None, err
    if resp and resp.get("message") == "OTP sent to your phone":
        ref = resp.get("data", {}).get("refrence_code")
        if ref:
            return ref, None
    return None, (resp.get("message", "Unknown") if resp else "No response")

def yoga_verify_otp(phone, ref, otp, did, sid):
    return yoga_api_post(YOGA_VERIFY_URL, {
        "phone": phone, "reference_code": ref, "otp": otp,
        "experimentMetaInfo": {"deviceId": did, "sessionId": sid},
        "registerUser": False,
    }, YOGA_HEADERS)

def rand_id():
    return str(uuid.uuid4())

def rand_yoga_name():
    return random.choice(YOGA_NAMES)

def extract_yoga_code(link: str):
    """Extract code from link OR accept direct code - FIXED"""
    link = link.strip().rstrip("/")
    
    # Check if it's a full URL
    if "habit.yoga/" in link:
        code = link.replace("https://habit.yoga/", "").replace("http://habit.yoga/", "")
        code = code.split("/")[0]  # Get first part after domain
        if code and all(c.isalnum() or c == "_" for c in code) and 1 <= len(code) <= 50:
            return code
        return None
    
    # Check if it's a direct code (alphanumeric + underscore)
    if link and all(c.isalnum() or c == "_" for c in link) and 1 <= len(link) <= 50:
        return link
    
    return None

# ==================== SHOPSY SESSION FUNCTIONS ====================
def save_shopsy_session(user_id, phone, session_data):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('REPLACE INTO shopsy_sessions (user_id, phone, session_data, updated_at) VALUES (?, ?, ?, ?)',
              (user_id, phone, json.dumps(session_data), datetime.now().isoformat()))
    conn.commit()
    conn.close()
    set_shopsy_login_status(user_id, 1)

def get_shopsy_session(user_id):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT phone, session_data FROM shopsy_sessions WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return row[0], json.loads(row[1])
    return None, None

def logout_shopsy_user(user_id):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT phone FROM users WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    phone = row[0] if row else None
    c.execute('DELETE FROM shopsy_sessions WHERE user_id = ?', (user_id,))
    c.execute('UPDATE users SET shopsy_is_logged_in = 0 WHERE user_id=?', (user_id,))
    conn.commit()
    conn.close()
    if phone:
        session_file = os.path.join(SHOPSY_SESSIONS_DIR, f"{phone}.json")
        if os.path.exists(session_file):
            try:
                os.remove(session_file)
            except:
                pass
    return True

# ==================== MEMBERSHIP ====================
def is_channel_member(user_id):
    try:
        member = bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

def check_membership(user_id):
    return is_channel_member(user_id)

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

def get_menu_kb(uid: int) -> ReplyKeyboardMarkup:
    is_admin = (uid == ADMIN_ID)
    if is_admin:
        kb = ReplyKeyboardMarkup(resize_keyboard=True, is_persistent=True)
        kb.row("✨ Start Workflow", "📊 Total Stats")
        kb.row("🔗 Bot Refer Link", "🔄 Code Update")
        kb.row("🧘 Yoga Referral", "💡 Help")
        kb.row("👑 Admin Panel")
        return kb
    else:
        kb = ReplyKeyboardMarkup(resize_keyboard=True, is_persistent=True)
        kb.row("✨ Start Workflow", "📊 Total Stats")
        kb.row("🔗 Bot Refer Link", "🔄 Code Update")
        kb.row("🧘 Yoga Referral", "💡 Help")
        return kb

# ==================== SHOPSY API FUNCTIONS ====================
def generate_ids():
    return uuid.uuid4().hex[:32], f"{uuid.uuid4().hex[:32]}-{int(time.time() * 1000)}", f"{uuid.uuid4()}_{int(time.time()*1000)}"

def save_session(phone, session_data):
    with open(os.path.join(SHOPSY_SESSIONS_DIR, f"{phone}.json"), "w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=2, ensure_ascii=False)

def update_session(session_data, resp_json, resp_headers):
    if isinstance(resp_json, dict):
        sess_block = resp_json.get("SESSION") or resp_json.get("RESPONSE", {}).get("SESSION") or {}
        for k in ["accountId", "at", "rt", "sn", "secureToken", "nsid", "vid", "email", "firstName", "lastName"]:
            if sess_block.get(k):
                session_data[k] = sess_block[k]
        if session_data.get("firstName"):
            session_data["userName"] = f"{session_data.get('firstName', '')} {session_data.get('lastName', '')}".strip()
        if sess_block.get("isLoggedIn") is not None:
            session_data["isLoggedIn"] = sess_block["isLoggedIn"]
    if resp_headers:
        headers_lower = {k.lower(): v for k, v in resp_headers.items()}
        for k in ["at", "rt", "sn", "nsid", "vid"]:
            if k in headers_lower:
                session_data[k] = headers_lower[k]
        if headers_lower.get("securecookie"):
            session_data["secureCookie"] = headers_lower.get("securecookie")
    return session_data

def sync_api_request(method, url_path, json_body, session_data, is_game=False):
    device_id = session_data.get("device_id") or uuid.uuid4().hex[:32]
    visit_id = session_data.get("visit_id") or f"{uuid.uuid4().hex[:32]}-{int(time.time() * 1000)}"
    app_sess = session_data.get("app_session_id") or f"{uuid.uuid4()}_{int(time.time()*1000)}"

    if is_game:
        headers = {
            "x-user-agent": f"Mozilla/5.0 (Linux; Android 9; OPPO:CPH2083 Build/{device_id[:13]}) FKUA/Retail/2291170/Android/Mobile (OPPO/OPPO:CPH2083/{device_id})",
            "sessionid": "session_id",
            "Content-Type": "application/json; charset=UTF-8",
            "User-Agent": "okhttp/4.9.2",
            "Accept-Encoding": "gzip",
            "Connection": "Keep-Alive",
            "city": "Delhi"
        }
    else:
        headers = {
            "X-PARTNER-CONTEXT": '{"source":"reseller"}',
            "FK-TENANT-ID": "SHOPSY",
            "business": "reseller",
            "Content-Type": "application/json; charset=UTF-8",
            "User-Agent": "okhttp/4.9.2",
            "X-User-Agent": f"Mozilla/5.0 (Linux; Android 9; CPH2083 Build/PPR1.180610.011) FKUA/Retail/2291170/Android/Mobile (OPPO/CPH2083/{device_id})",
            "X-Visit-Id": visit_id,
            "Accept-Encoding": "gzip",
            "Connection": "Keep-Alive",
            "city": "Delhi",
            "X-AppSession-ID": app_sess
        }
        for k in ["at", "sn", "secureToken"]:
            if session_data.get(k):
                headers[k] = session_data[k]

    req_session = cffi_requests.Session(impersonate="chrome110")

    for attempt in range(1, 4):
        dc = session_data.get("current_dc", "1")
        url = f"https://{dc}.rome.api.flipkart.net{url_path}"
        try:
            resp = req_session.post(url, json=json_body, headers=headers, timeout=30, verify=False) if method == "POST" else req_session.get(url, headers=headers, timeout=30, verify=False)

            try:
                resp_json = resp.json()
            except:
                resp_json = {}

            if resp.status_code == 406 and resp_json.get("ERROR_MESSAGE") == "DC Change":
                new_dc = resp_json.get("RESPONSE", {}).get("id") or resp_json.get("RESPONSE", {}).get("dc")
                if new_dc:
                    session_data["current_dc"] = str(new_dc)
                    continue

            return resp.status_code, resp_json, dict(resp.headers), session_data
        except Exception as e:
            if attempt == 3:
                return 500, {"error": str(e)}, {}, session_data
            time.sleep(2)

    return 500, {"error": "Max retries"}, {}, session_data

async def run_sh_user_state(session_data):
    body = {
        "location": {"pincode": None},
        "ad": {"adId": str(uuid.uuid4()), "doNotPersonalizeAds": False, "sdkAdId": "", "adSdkVersion": "2.12.0"},
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
    st, resp_json, headers, session_data = await asyncio.to_thread(sync_api_request, "POST", "/4/user/state", body, session_data, False)
    return update_session(session_data, resp_json, headers)

async def get_user_info_tg(session_data):
    body = {
        "requestMethod": "GET",
        "routeUri": "user/get-user",
        "payload": {"userId": session_data.get("accountId", ""), "userName": session_data.get("userName", "User")}
    }
    st, resp_json, headers, session_data = await asyncio.to_thread(sync_api_request, "POST", "/1/shopsy/games", body, session_data, True)
    if st == 200 and isinstance(resp_json, dict) and resp_json.get("success"):
        return resp_json["data"]
    return None

async def get_config_tg(session_data):
    body = {"requestMethod": "GET", "routeUri": "config/get-config", "payload": {}}
    st, resp_json, headers, session_data = await asyncio.to_thread(sync_api_request, "POST", "/1/shopsy/games", body, session_data, True)
    if st == 200 and isinstance(resp_json, dict) and resp_json.get("success"):
        return resp_json["data"]
    return None

async def claim_gullak_tg(session_data):
    body = {
        "requestMethod": "POST",
        "routeUri": "gullak/claim-gullak",
        "payload": {"userId": session_data.get("accountId", "")}
    }
    await asyncio.to_thread(sync_api_request, "POST", "/1/shopsy/games", body, session_data, True)

async def start_game_tg(session_data, game_id):
    body = {
        "requestMethod": "POST",
        "routeUri": "game/game-started",
        "payload": {"userId": session_data.get("accountId", ""), "gameId": game_id}
    }
    st, resp_json, headers, session_data = await asyncio.to_thread(sync_api_request, "POST", "/1/shopsy/games", body, session_data, True)
    if st == 200 and isinstance(resp_json, dict) and resp_json.get("success"):
        return resp_json["data"].get("sessionId"), resp_json["data"]
    return None, resp_json

async def end_game_tg(session_data, game_id, game_session_id, play_time, gems_earned):
    body = {
        "requestMethod": "POST",
        "routeUri": "game/game-ended",
        "payload": {
            "userId": session_data.get("accountId", ""),
            "gameId": game_id,
            "sessionId": game_session_id,
            "gemsEarned": gems_earned,
            "playTimeInSec": play_time
        }
    }
    st, resp_json, headers, session_data = await asyncio.to_thread(sync_api_request, "POST", "/1/shopsy/games", body, session_data, True)
    if st == 200 and isinstance(resp_json, dict) and resp_json.get("success"):
        return resp_json["data"]
    return None

async def login_with_otp(phone):
    print(f"[SHOPSY] Logging in with +91{phone}...")
    d_id, v_id, s_id = generate_ids()
    session_data = {
        "phone": phone,
        "device_id": d_id,
        "visit_id": v_id,
        "app_session_id": s_id,
        "current_dc": "1",
        "owner_id": "telegram_bot",
        "last_refresh": time.time()
    }

    body = {
        "actionRequestContext": {
            "type": "LOGIN_IDENTITY_VERIFY_SHOPSY2",
            "loginId": phone,
            "loginIdPrefix": "+91",
            "phoneNumberFormat": "E164",
            "addAppHash": True,
            "loginType": "MOBILE",
            "verificationType": "OTP",
            "sourceContext": "DEFAULT",
            "clientQueryParamMap": None
        }
    }
    st, resp, hdrs, session_data = await asyncio.to_thread(sync_api_request, "POST", "/1/action/view", body, session_data, False)
    if st != 200 or not isinstance(resp, dict):
        return None, f"OTP request failed (HTTP {st})"
    session_data = update_session(session_data, resp, hdrs)
    req_id = resp.get("RESPONSE", {}).get("actionResponseContext", {}).get("requestId") or resp.get("requestId")
    if not req_id:
        return None, "No request ID in response"
    session_data["otpRequestId"] = req_id
    return session_data, "OTP sent"

async def verify_otp(session_data, otp):
    phone = session_data.get("phone")
    body = {
        "actionRequestContext": {
            "type": "LOGIN_SHOPSY2",
            "loginId": phone,
            "loginIdPrefix": "+91",
            "password": None,
            "otp": otp,
            "otpRequestId": session_data.get("otpRequestId"),
            "remainingAttempts": 5,
            "phoneNumberFormat": "E164",
            "loginType": "MOBILE",
            "verificationType": "OTP",
            "sourceContext": "DEFAULT",
            "churned": False
        }
    }
    st, resp, hdrs, session_data = await asyncio.to_thread(sync_api_request, "POST", "/1/action/view", body, session_data, False)
    if st == 200 and isinstance(resp, dict) and resp.get("RESPONSE", {}).get("actionResponseContext", {}).get("authenticationSuccess", False):
        session_data = update_session(session_data, resp, hdrs)
        session_data["isLoggedIn"] = True
        session_data["last_refresh"] = time.time()
        return session_data, True
    return session_data, False

async def refresh_session_once(session_data):
    phone = session_data.get("phone")
    try:
        session_data = await run_sh_user_state(session_data)
        session_data["last_refresh"] = time.time()
        save_session(phone, session_data)
        return session_data
    except Exception as e:
        print(f"Session refresh error: {e}")
        return session_data

async def core_mine_logic(session_data, progress_callback=None):
    phone = session_data.get("phone")
    
    if progress_callback:
        await progress_callback("🔄 Refreshing session...")
    session_data = await refresh_session_once(session_data)
    
    if progress_callback:
        await progress_callback("🔄 Fetching user state...")
    session_data = await run_sh_user_state(session_data)
    save_session(phone, session_data)

    if progress_callback:
        await progress_callback("💰 Getting balance...")
    initial_user_data = await get_user_info_tg(session_data)
    if not initial_user_data:
        return {"status": "fail", "earned": 0, "msg": "Session expired. Please re-login."}
    
    initial_coins = initial_user_data.get("earnings", {}).get("coinsEarnedTotal", 0)

    if progress_callback:
        await progress_callback("🎁 Claiming gullak...")
    await claim_gullak_tg(session_data)

    if progress_callback:
        await progress_callback("🎮 Fetching available games...")
    config_data = await get_config_tg(session_data)
    games = config_data.get("games", []) if config_data else []
    
    if not games:
        return {"status": "fail", "earned": 0, "msg": "No active games"}

    total = len(games)
    played_count = 0
    total_gems = 0
    
    for i, g in enumerate(games):
        game_id = g.get("id")
        game_name = g.get("name", game_id)
        
        if progress_callback:
            await progress_callback(f"🎮 Starting {game_name} ({i+1}/{total})...")
        
        game_sess_id, _ = await start_game_tg(session_data, game_id)
        if game_sess_id:
            wait = random.randint(10, 13)
            
            for sec in range(wait, 0, -1):
                if progress_callback and sec % 3 == 0:
                    await progress_callback(f"⏳ Playing {game_name}... {sec}s remaining")
                await asyncio.sleep(1)
            
            gems = random.randint(3000, 5000)
            end_data = await end_game_tg(session_data, game_id, game_sess_id, wait, gems)
            if end_data:
                played_count += 1
                total_gems += gems
                if progress_callback:
                    await progress_callback(f"✅ Earned {gems} gems from {game_name}")
            else:
                if progress_callback:
                    await progress_callback(f"⚠️ Failed to complete {game_name}")
        else:
            if progress_callback:
                await progress_callback(f"❌ Could not start {game_name}")
        await asyncio.sleep(0.5)

    save_session(phone, session_data)

    if progress_callback:
        await progress_callback("📊 Finalizing balance...")
    final_user_data = await get_user_info_tg(session_data)
    final_coins = final_user_data.get("earnings", {}).get("coinsEarnedTotal", 0) if final_user_data else initial_coins
    earned = max(0, final_coins - initial_coins)

    return {
        "status": "success", 
        "earned": earned, 
        "final_coins": final_coins, 
        "played": played_count, 
        "total": total,
        "gems": total_gems,
        "time_taken": (wait * total) if total > 0 else 0
    }

# ==================== SHOPSY HANDLERS ====================
@bot.message_handler(func=lambda message: user_shopsy_state.get(message.from_user.id) == "waiting_phone")
def shopsy_phone_handler(message):
    user_id = message.from_user.id
    phone = message.text.strip()
    
    # Check for cancellation
    if phone.lower() in ['/cancel', 'cancel', 'abort']:
        user_shopsy_state[user_id] = None
        bot.reply_to(message, "❌ Shopsy mining cancelled.", reply_markup=get_menu_kb(user_id))
        return
    
    if not phone.isdigit() or len(phone) != 10:
        bot.reply_to(message, "❌ Please enter exactly 10 digits.\n\nSend /cancel to abort.")
        return
    
    cost = get_module_cost("shopsy")
    balance = get_user_balance(user_id)
    if balance < cost:
        bot.reply_to(message, f"❌ Insufficient credits! You need {cost} credits. Your balance: {balance}")
        return
    
    # Create abort keyboard
    abort_kb = InlineKeyboardMarkup()
    abort_kb.add(InlineKeyboardButton("❌ Abort", callback_data="shopsy_abort"))
    
    status_msg = bot.reply_to(message, f"📱 Sending OTP to +91{phone}...", reply_markup=abort_kb)
    
    # Deduct credits (will be refunded on failure)
    update_user_balance(user_id, -cost)
    
    def send_otp_thread():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            session_data, msg = loop.run_until_complete(login_with_otp(phone))
            loop.close()
            
            if not session_data:
                update_user_balance(user_id, cost)  # REFUND
                bot.edit_message_text(f"❌ Failed: {msg}", chat_id=message.chat.id, message_id=status_msg.message_id)
                user_shopsy_state[user_id] = None
                return
            
            user_shopsy_otp_data[user_id] = {"session_data": session_data, "phone": phone, "cost": cost}
            user_shopsy_state[user_id] = "waiting_otp"
            
            # OTP waiting with abort button
            otp_kb = InlineKeyboardMarkup()
            otp_kb.add(InlineKeyboardButton("❌ Abort", callback_data="shopsy_abort_otp"))
            
            bot.edit_message_text(
                f"✅ OTP sent to +91{phone}!\n\n"
                f"Enter the OTP code you received:\n\nSend /cancel to abort.",
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                reply_markup=otp_kb
            )
        except Exception as e:
            update_user_balance(user_id, cost)  # REFUND
            bot.edit_message_text(f"❌ Error: {str(e)[:200]}", chat_id=message.chat.id, message_id=status_msg.message_id)
            user_shopsy_state[user_id] = None
    
    threading.Thread(target=send_otp_thread).start()

@bot.callback_query_handler(func=lambda call: call.data in ["shopsy_abort", "shopsy_abort_otp"])
def shopsy_abort_callback(call):
    user_id = call.from_user.id
    
    if call.data == "shopsy_abort_otp":
        data = user_shopsy_otp_data.get(user_id, {})
        cost = data.get("cost", get_module_cost("shopsy"))
        
        if user_shopsy_state.get(user_id) == "waiting_otp":
            update_user_balance(user_id, cost)  # REFUND
            user_shopsy_state[user_id] = None
            user_shopsy_otp_data.pop(user_id, None)
            bot.edit_message_text(
                "🔄 OTP session aborted. Credits refunded.",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id
            )
            bot.answer_callback_query(call.id, "✅ Aborted")
            return
    
    elif call.data == "shopsy_abort":
        if user_shopsy_state.get(user_id) == "waiting_phone":
            cost = get_module_cost("shopsy")
            update_user_balance(user_id, cost)  # REFUND
            user_shopsy_state[user_id] = None
            bot.edit_message_text(
                "🔄 Shopsy mining aborted. Credits refunded.",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id
            )
            bot.answer_callback_query(call.id, "✅ Aborted")
            return
    
    bot.answer_callback_query(call.id, "No active session")

@bot.message_handler(func=lambda message: user_shopsy_state.get(message.from_user.id) == "waiting_otp")
def shopsy_otp_handler(message):
    user_id = message.from_user.id
    otp = message.text.strip()
    
    if otp.lower() in ['/cancel', 'cancel']:
        data = user_shopsy_otp_data.get(user_id, {})
        cost = data.get("cost", get_module_cost("shopsy"))
        update_user_balance(user_id, cost)  # REFUND
        user_shopsy_state[user_id] = None
        user_shopsy_otp_data.pop(user_id, None)
        bot.reply_to(message, "🔄 OTP verification cancelled. Credits refunded.")
        return
    
    if not otp.isdigit():
        bot.reply_to(message, "❌ Enter a valid OTP.\n\nSend /cancel to abort.")
        return
    
    data = user_shopsy_otp_data.get(user_id)
    if not data:
        bot.reply_to(message, "❌ Session expired. Start over.")
        user_shopsy_state[user_id] = None
        return
    
    session_data = data["session_data"]
    phone = data["phone"]
    cost = data.get("cost", get_module_cost("shopsy"))
    
    status_msg = bot.reply_to(message, "🔐 Verifying OTP...")
    
    def verify_thread():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            verified_session, success = loop.run_until_complete(verify_otp(session_data, otp))
            loop.close()
            
            if success:
                save_shopsy_session(user_id, phone, verified_session)
                save_session(phone, verified_session)
                user_shopsy_state[user_id] = "mining"
                
                bot.edit_message_text(
                    f"✅ **Login successful!**\n\n📞 +91{phone}\n\nStarting mining...",
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id
                )
                
                start_shopsy_mining(message, user_id, phone, verified_session)
            else:
                update_user_balance(user_id, cost)  # REFUND
                bot.edit_message_text(
                    "❌ Invalid OTP. Credits refunded. Please try again.",
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id
                )
                user_shopsy_state[user_id] = None
                user_shopsy_otp_data.pop(user_id, None)
        except Exception as e:
            update_user_balance(user_id, cost)  # REFUND
            bot.edit_message_text(f"❌ Error: {str(e)[:200]}", chat_id=message.chat.id, message_id=status_msg.message_id)
            user_shopsy_state[user_id] = None
            user_shopsy_otp_data.pop(user_id, None)
    
    threading.Thread(target=verify_thread).start()

def start_shopsy_mining(message, user_id, phone, session_data):
    progress_msg = bot.reply_to(message, "⛏️ **Shopsy Mining Started...**\n\n⏳ Please wait (1-2 minutes)")
    
    async def update_progress(msg):
        try:
            bot.edit_message_text(f"⛏️ **Shopsy Mining...**\n\n{msg}", 
                                chat_id=message.chat.id, 
                                message_id=progress_msg.message_id)
        except:
            pass
    
    def mine_thread():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(core_mine_logic(session_data, update_progress))
            loop.close()
            
            if result["status"] == "success":
                points = result["earned"] // 100
                update_shopsy_balance(user_id, points)
                
                conn = sqlite3.connect(DB_PATH, check_same_thread=False)
                c = conn.cursor()
                c.execute('INSERT INTO shopsy_mining_history (user_id, phone, coins_earned, games_played, gems_earned, time_taken) VALUES (?, ?, ?, ?, ?, ?)',
                         (user_id, phone, result["earned"], result["played"], result.get("gems", 0), result.get("time_taken", 0)))
                conn.commit()
                conn.close()
                
                bot.edit_message_text(
                    f"✅ **Shopsy Mining Complete!**\n\n"
                    f"🪙 Coins Earned: {result['earned']}\n"
                    f"⭐ Points Earned: +{points}\n"
                    f"🎮 Games Played: {result['played']}/{result['total']}\n"
                    f"💎 Gems Earned: {result.get('gems', 0)}\n"
                    f"⏱️ Time Taken: {result.get('time_taken', 0)} seconds\n"
                    f"📊 Total Shopsy Points: {get_shopsy_balance(user_id)}",
                    chat_id=message.chat.id,
                    message_id=progress_msg.message_id
                )
                log_usage(user_id, "Shopsy Mining", f"Phone: +91{phone}")
            else:
                cost = get_module_cost("shopsy")
                update_user_balance(user_id, cost)  # REFUND
                bot.edit_message_text(
                    f"❌ **Shopsy Mining Failed**\n\n{result.get('msg', 'Unknown error')}\n\nCredits refunded.",
                    chat_id=message.chat.id,
                    message_id=progress_msg.message_id
                )
            
            user_shopsy_state[user_id] = None
            user_shopsy_otp_data.pop(user_id, None)
            
        except Exception as e:
            cost = get_module_cost("shopsy")
            update_user_balance(user_id, cost)  # REFUND
            bot.edit_message_text(f"❌ Error: {str(e)[:200]}", chat_id=message.chat.id, message_id=progress_msg.message_id)
            user_shopsy_state[user_id] = None
            user_shopsy_otp_data.pop(user_id, None)
    
    threading.Thread(target=mine_thread).start()

# ==================== SHOPSY CALLBACK HANDLER ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith("shopsy_"))
def handle_shopsy_callback(call):
    user_id = call.from_user.id
    action = call.data.split("_")[1]
    
    bot.answer_callback_query(call.id)
    
    if action == "start":
        cost = get_module_cost("shopsy")
        balance = get_user_balance(user_id)
        if balance < cost:
            bot.send_message(call.message.chat.id, f"❌ You need {cost} credits for Shopsy mining!")
            return
        
        user_shopsy_state[user_id] = "waiting_phone"
        bot.edit_message_text(
            f"🎯 **SHOPSY MINING**\n\n"
            f"Enter your 10‑digit phone number (without country code).\n"
            f"I will send an OTP to that number.\n\n"
            f"💰 Cost: <b>{cost} Credits</b>\n"
            f"⏱️ Process takes 1-2 minutes.\n\n"
            f"Send /cancel to abort.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="HTML"
        )
    
    elif action == "stats":
        shopsy_bal = get_shopsy_balance(user_id)
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM shopsy_mining_history WHERE user_id = ?', (user_id,))
        total_runs = c.fetchone()[0]
        c.execute('SELECT SUM(coins_earned) FROM shopsy_mining_history WHERE user_id = ?', (user_id,))
        total_coins = c.fetchone()[0] or 0
        conn.close()
        
        bot.edit_message_text(
            f"📊 **Shopsy Mining Stats**\n\n"
            f"🪙 Total Coins Mined: {total_coins}\n"
            f"⭐ Shopsy Points: {shopsy_bal}\n"
            f"📊 Total Runs: {total_runs}\n\n"
            f"💡 Each run costs {get_module_cost('shopsy')} credits.\n"
            f"You earn points based on coins mined!",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=shopsy_menu_keyboard(),
            parse_mode="HTML"
        )
    
    elif action == "logout":
        logout_shopsy_user(user_id)
        bot.edit_message_text(
            "🚪 **Logged out from Shopsy**\n\n"
            "Your Shopsy session has been cleared.\n"
            "You can login again anytime.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=shopsy_menu_keyboard(),
            parse_mode="HTML"
        )

# ==================== YOGA HANDLERS ====================

@bot.message_handler(func=lambda message: user_yoga_state.get(message.from_user.id) == "waiting_code")
def yoga_code_handler(message):
    user_id = message.from_user.id
    text = message.text.strip()
    code = extract_yoga_code(text)
    
    if not code:
        bot.reply_to(message, "❌ *Invalid Yoga code!*\n\nSend your Habit.Yoga referral link or code:\n`https://habit.yoga/yourcode`\nor just: `yourcode`", parse_mode="Markdown")
        return
    
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('UPDATE users SET yoga_code = ? WHERE user_id = ?', (code, user_id))
    conn.commit()
    conn.close()
    
    user_yoga_state[user_id] = None
    bot.reply_to(message, f"✅ *Yoga Code Saved!*\n\nYour code: `{code}`\n\nNow use the Yoga module to start referring!", parse_mode="Markdown", reply_markup=get_menu_kb(user_id))

@bot.message_handler(func=lambda message: user_yoga_state.get(message.from_user.id) == "waiting_phone")
def yoga_phone_handler(message):
    user_id = message.from_user.id
    phone = message.text.strip().replace(" ", "")
    
    # Check for cancellation
    if phone.lower() in ['/cancel', 'cancel']:
        user_yoga_state[user_id] = None
        bot.reply_to(message, "❌ Yoga referral cancelled.", reply_markup=get_menu_kb(user_id))
        return
    
    if not phone.isdigit() or len(phone) != 10:
        bot.reply_to(message, "❌ *Invalid number!* Need 10 digits.\n\nSend `/cancel` to abort.", parse_mode="Markdown")
        return
    
    cost = get_module_cost("yoga")
    balance = get_user_balance(user_id)
    if balance < cost:
        bot.reply_to(message, f"❌ *Insufficient points!* Need {cost} points.\n\n💡 Earn more by sharing your bot link!", parse_mode="Markdown")
        return
    
    # Create abort keyboard
    abort_kb = InlineKeyboardMarkup()
    abort_kb.add(InlineKeyboardButton("❌ Abort", callback_data="yoga_abort"))
    
    phone_full = f"+91{phone}"
    status_msg = bot.reply_to(message, f"⏳ *Processing...*\n📱 `{phone_full}`", parse_mode="Markdown", reply_markup=abort_kb)
    
    # Deduct credits (will be refunded on failure)
    update_user_balance(user_id, -cost)
    
    def yoga_register_thread():
        try:
            did, sid = rand_id(), rand_id()
            name = rand_yoga_name()
            
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute('SELECT yoga_code FROM users WHERE user_id = ?', (user_id,))
            row = c.fetchone()
            conn.close()
            yoga_code = row[0] if row else None
            
            if not yoga_code:
                update_user_balance(user_id, cost)  # REFUND
                bot.edit_message_text(
                    "❌ *No Yoga code set!* Use the Yoga module to set code first.",
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id,
                    parse_mode="Markdown"
                )
                user_yoga_state[user_id] = None
                return
            
            resp, err = yoga_register(phone_full, yoga_code, name, did, sid)
            
            if err or not resp:
                update_user_balance(user_id, cost)  # REFUND
                bot.edit_message_text(
                    f"❌ *Registration failed!*\n{err or 'No response'}",
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id,
                    parse_mode="Markdown"
                )
                user_yoga_state[user_id] = None
                return
            
            is_verified = resp.get("result", {}).get("data", {}).get("account", {}).get("is_phone_number_verified", False)
            
            if is_verified:
                update_user_balance(user_id, cost)  # REFUND
                bot.edit_message_text(
                    f"⚠️ *Number already registered!*\n📱 `{phone_full}`",
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id,
                    parse_mode="Markdown"
                )
                user_yoga_state[user_id] = None
                return
            
            otp_did, otp_sid = rand_id(), rand_id()
            otp_ref, err = yoga_send_otp(phone_full, otp_did, otp_sid)
            
            if err or not otp_ref:
                update_user_balance(user_id, cost)  # REFUND
                bot.edit_message_text(
                    f"⚠️ *OTP failed!*\n{err or 'No reference'}",
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id,
                    parse_mode="Markdown"
                )
                user_yoga_state[user_id] = None
                return
            
            user_yoga_otp_data[user_id] = {
                "phone": phone_full,
                "otp_ref": otp_ref,
                "otp_did": otp_did,
                "otp_sid": otp_sid,
                "name": name,
                "cost": cost
            }
            user_yoga_state[user_id] = "waiting_otp"
            
            # OTP waiting with abort button
            otp_kb = InlineKeyboardMarkup()
            otp_kb.add(InlineKeyboardButton("❌ Abort", callback_data="yoga_abort_otp"))
            
            bot.edit_message_text(
                f"✅ *OTP Sent!*\n📱 `{phone_full}`\n\n🔐 *Enter 6-digit OTP:*\n\nSend `/cancel` to abort.",
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                parse_mode="Markdown",
                reply_markup=otp_kb
            )
            
        except Exception as e:
            update_user_balance(user_id, cost)  # REFUND
            bot.edit_message_text(
                f"❌ *Error:* {str(e)[:200]}",
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                parse_mode="Markdown"
            )
            user_yoga_state[user_id] = None
    
    threading.Thread(target=yoga_register_thread).start()

@bot.callback_query_handler(func=lambda call: call.data in ["yoga_abort", "yoga_abort_otp"])
def yoga_abort_callback(call):
    user_id = call.from_user.id
    
    if call.data == "yoga_abort_otp":
        data = user_yoga_otp_data.get(user_id, {})
        cost = data.get("cost", get_module_cost("yoga"))
        
        if user_yoga_state.get(user_id) == "waiting_otp":
            update_user_balance(user_id, cost)  # REFUND
            user_yoga_state[user_id] = None
            user_yoga_otp_data.pop(user_id, None)
            bot.edit_message_text(
                "🔄 *OTP session aborted.* Credits refunded.",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode="Markdown"
            )
            bot.answer_callback_query(call.id, "✅ Aborted")
            return
    
    elif call.data == "yoga_abort":
        if user_yoga_state.get(user_id) == "waiting_phone":
            cost = get_module_cost("yoga")
            update_user_balance(user_id, cost)  # REFUND
            user_yoga_state[user_id] = None
            bot.edit_message_text(
                "🔄 *Yoga referral aborted.* Credits refunded.",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode="Markdown"
            )
            bot.answer_callback_query(call.id, "✅ Aborted")
            return
    
    bot.answer_callback_query(call.id, "No active session")

@bot.message_handler(func=lambda message: user_yoga_state.get(message.from_user.id) == "waiting_otp")
def yoga_otp_handler(message):
    user_id = message.from_user.id
    otp = message.text.strip()
    
    if otp.lower() in ['/cancel', 'cancel']:
        data = user_yoga_otp_data.get(user_id, {})
        cost = data.get("cost", get_module_cost("yoga"))
        update_user_balance(user_id, cost)  # REFUND
        user_yoga_state[user_id] = None
        user_yoga_otp_data.pop(user_id, None)
        bot.reply_to(message, "🔄 *OTP verification cancelled.* Credits refunded.", parse_mode="Markdown")
        return
    
    if not otp.isdigit() or len(otp) != 6:
        bot.reply_to(message, "❌ *Need 6-digit OTP!* Try again:\n\nSend `/cancel` to abort.", parse_mode="Markdown")
        return
    
    data = user_yoga_otp_data.get(user_id)
    if not data:
        bot.reply_to(message, "❌ *Session expired.* Use Yoga module again.", parse_mode="Markdown")
        user_yoga_state[user_id] = None
        return
    
    phone = data["phone"]
    otp_ref = data["otp_ref"]
    did = data["otp_did"]
    sid = data["otp_sid"]
    name = data.get("name", "User")
    cost = data.get("cost", get_module_cost("yoga"))
    
    status_msg = bot.reply_to(message, "⏳ *Verifying OTP...*", parse_mode="Markdown")
    
    def yoga_verify_thread():
        try:
            result, err = yoga_verify_otp(phone, otp_ref, otp, did, sid)
            
            if err or not result:
                update_user_balance(user_id, cost)  # REFUND
                bot.edit_message_text(
                    f"❌ *Invalid or Expired OTP!*\n{err or 'Failed'}\n\nCredits refunded.",
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id,
                    parse_mode="Markdown"
                )
                user_yoga_state[user_id] = None
                user_yoga_otp_data.pop(user_id, None)
                return
            
            reward = get_yoga_refer_reward()
            update_user_balance(user_id, reward)
            
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute('UPDATE users SET yoga_refers = yoga_refers + 1 WHERE user_id = ?', (user_id,))
            conn.commit()
            conn.close()
            
            new_balance = get_user_balance(user_id)
            
            bot.edit_message_text(
                f"🎉 *YOGA REFERRAL COMPLETE!* 🎉\n\n"
                f"✅ *Referee:* {name}\n"
                f"📱 *Phone:* `{phone}`\n"
                f"💰 *Points Earned:* +{reward}\n"
                f"📊 *Your Balance:* `{new_balance}`\n\n"
                f"Ready for another? Use the Yoga module!",
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                parse_mode="Markdown"
            )
            
            log_usage(user_id, "Yoga Referral", f"Phone: {phone}")
            user_yoga_state[user_id] = None
            user_yoga_otp_data.pop(user_id, None)
            
        except Exception as e:
            update_user_balance(user_id, cost)  # REFUND
            bot.edit_message_text(
                f"❌ *Error:* {str(e)[:200]}\n\nCredits refunded.",
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                parse_mode="Markdown"
            )
            user_yoga_state[user_id] = None
            user_yoga_otp_data.pop(user_id, None)
    
    threading.Thread(target=yoga_verify_thread).start()

# ==================== YOGA CALLBACK HANDLER ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith("yoga_"))
def handle_yoga_callback(call):
    user_id = call.from_user.id
    action = call.data.split("_")[1]
    
    bot.answer_callback_query(call.id)
    
    if action == "start":
        cost = get_module_cost("yoga")
        balance = get_user_balance(user_id)
        
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('SELECT yoga_code FROM users WHERE user_id = ?', (user_id,))
        row = c.fetchone()
        conn.close()
        
        if not row or not row[0]:
            bot.edit_message_text(
                "🧘 *Yoga Referral Setup*\n\n"
                "First, set your Habit.Yoga referral code.\n"
                "Send your referral link or code:\n"
                "`https://habit.yoga/yourcode`\n\n"
                "Or just: `yourcode`",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode="Markdown"
            )
            user_yoga_state[user_id] = "waiting_code"
            return
        
        if balance < cost:
            bot.edit_message_text(
                f"❌ *Insufficient points!*\nNeed {cost} points.\n\n💡 Earn more by sharing your bot link!",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode="Markdown"
            )
            return
        
        bot.edit_message_text(
            f"🧘 *Yoga Referral*\n\n"
            f"💰 Cost: <b>{cost} Credits</b>\n"
            f"🎁 Reward: <b>{get_yoga_refer_reward()} Credits</b> per referral\n\n"
            f"📱 Send 10-digit phone number:\n\nSend `/cancel` to abort.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="HTML"
        )
        user_yoga_state[user_id] = "waiting_phone"
    
    elif action == "stats":
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('SELECT yoga_refers FROM users WHERE user_id = ?', (user_id,))
        row = c.fetchone()
        conn.close()
        yoga_refers = row[0] if row else 0
        
        balance = get_user_balance(user_id)
        cost = get_module_cost("yoga")
        reward = get_yoga_refer_reward()
        
        bot.edit_message_text(
            f"🧘 *Your Yoga Stats*\n\n"
            f"💰 Balance: `{balance}`\n"
            f"🎯 Yoga Refers: `{yoga_refers}`\n"
            f"💡 Cost per refer: `{cost}`\n"
            f"🎁 Reward per refer: `{reward}`\n\n"
            f"Use the Yoga module to start referring!",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=yoga_menu_keyboard(),
            parse_mode="Markdown"
        )
    
    elif action == "setcode":
        bot.edit_message_text(
            "🧘 *Set Yoga Code*\n\n"
            "Send your Habit.Yoga referral link or code:\n"
            "`https://habit.yoga/yourcode`\n\n"
            "Or just: `yourcode`",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown"
        )
        user_yoga_state[user_id] = "waiting_code"

# ==================== TEMP MAIL CLASS ====================
class TempMailBot:
    def __init__(self):
        self.base_url = "https://api.mail.tm"
        self.email = None
        self.password = None
        self.token = None
        self.account_id = None
        self.messages = []
        self.is_waiting = False
        self.expiry_time = None

    def generate_email(self):
        try:
            domains_res = requests.get(f"{self.base_url}/domains", timeout=10)
            domains = domains_res.json().get('hydra:member', [])
            if not domains:
                return {'success': False, 'error': 'No domains available'}
            domain = domains[0]['domain']
            username = 'user_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            address = f"{username}@{domain}"
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            account_res = requests.post(
                f"{self.base_url}/accounts",
                json={'address': address, 'password': password},
                headers={'Content-Type': 'application/json'}
            )
            if account_res.status_code != 201:
                return {'success': False, 'error': 'Account creation failed'}
            account = account_res.json()
            token_res = requests.post(
                f"{self.base_url}/token",
                json={'address': address, 'password': password},
                headers={'Content-Type': 'application/json'}
            )
            token_data = token_res.json()
            self.email = address
            self.password = password
            self.token = token_data.get('token')
            self.account_id = account.get('id')
            self.messages = []
            self.expiry_time = datetime.now() + timedelta(minutes=10)
            return {'success': True, 'email': address, 'expires': '10 minutes'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def check_inbox(self):
        if not self.token:
            return []
        try:
            response = requests.get(
                f"{self.base_url}/messages",
                headers={'Authorization': f'Bearer {self.token}'}
            )
            if response.status_code == 200:
                data = response.json()
                messages = data.get('hydra:member', [])
                for msg in messages:
                    if msg not in self.messages:
                        self.messages.append(msg)
                return messages
            return []
        except:
            return []

    def get_message_content(self, message_id):
        try:
            response = requests.get(
                f"{self.base_url}/messages/{message_id}",
                headers={'Authorization': f'Bearer {self.token}'}
            )
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None

    def get_otp_from_messages(self):
        self.check_inbox()
        for msg in self.messages:
            if 'body' not in msg:
                full_msg = self.get_message_content(msg['id'])
                if full_msg:
                    msg['body'] = full_msg.get('text', '')
                    msg['html'] = full_msg.get('html', '')
            body = msg.get('body', '') + msg.get('html', '')
            subject = msg.get('subject', '')
            combined = body + " " + subject
            patterns = [
                r'\b\d{4,6}\b',
                r'OTP[:\s]*(\d{4,6})',
                r'code[:\s]*(\d{4,6})',
                r'verification[:\s]*(\d{4,6})',
                r'pin[:\s]*(\d{4,6})',
                r'(\d{4,6})\s*is your'
            ]
            for pattern in patterns:
                matches = re.findall(pattern, combined, re.IGNORECASE)
                if matches:
                    otp = matches[0] if isinstance(matches[0], str) else matches[0]
                    from_addr = msg.get('from', {}).get('address', 'Unknown')
                    from_name = msg.get('from', {}).get('name', '')
                    return {
                        'otp': otp,
                        'from': from_addr,
                        'from_name': from_name,
                        'subject': subject,
                        'body': body[:500],
                        'time': datetime.now().strftime('%H:%M:%S')
                    }
        return None

    def wait_for_otp(self, callback, timeout=120):
        self.is_waiting = True
        start_time = time.time()
        checked_ids = set()
        initial = self.check_inbox()
        for msg in initial:
            checked_ids.add(msg['id'])
        while self.is_waiting and (time.time() - start_time) < timeout:
            try:
                messages = self.check_inbox()
                for msg in messages:
                    if msg['id'] not in checked_ids:
                        checked_ids.add(msg['id'])
                        full_msg = self.get_message_content(msg['id'])
                        if full_msg:
                            body = full_msg.get('text', '') + full_msg.get('html', '')
                            subject = full_msg.get('subject', '')
                            combined = body + " " + subject
                            patterns = [
                                r'\b\d{4,6}\b',
                                r'OTP[:\s]*(\d{4,6})',
                                r'code[:\s]*(\d{4,6})',
                                r'verification[:\s]*(\d{4,6})',
                                r'pin[:\s]*(\d{4,6})',
                                r'(\d{4,6})\s*is your'
                            ]
                            for pattern in patterns:
                                matches = re.findall(pattern, combined, re.IGNORECASE)
                                if matches:
                                    otp = matches[0] if isinstance(matches[0], str) else matches[0]
                                    self.is_waiting = False
                                    from_addr = full_msg.get('from', {}).get('address', 'Unknown')
                                    from_name = full_msg.get('from', {}).get('name', '')
                                    callback({
                                        'otp': otp,
                                        'from': from_addr,
                                        'from_name': from_name,
                                        'subject': subject,
                                        'body': body[:500],
                                        'time': datetime.now().strftime('%H:%M:%S')
                                    })
                                    return
            except:
                pass
            time.sleep(2)
        self.is_waiting = False
        callback(None)

# ==================== FLIPKART CHECKER ====================
def check_flipkart(num):
    try:
        num_with_code = "+91" + num 
        burp0_url = "https://1.rome.api.flipkart.com/api/6/user/signup/status"
        burp0_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0", 
            "Accept": "*/*", 
            "Accept-Language": "en-US,en;q=0.5", 
            "Accept-Encoding": "gzip, deflate", 
            "Content-Type": "application/json", 
            "Referer": "https://www.flipkart.com/", 
            "X-User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0 FKUA/website/42/website/Desktop", 
            "Origin": "https://www.flipkart.com", 
            "Sec-Fetch-Dest": "empty", 
            "Sec-Fetch-Mode": "cors", 
            "Sec-Fetch-Site": "same-site", 
            "Te": "trailers", 
            "Connection": "close"
        }
        burp0_json = {"loginId": [num_with_code], "supportAllStates": True}
        
        # Use proxy for Flipkart
        proxy_url = get_flipkart_proxy()
        proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None
        
        response = requests.post(burp0_url, headers=burp0_headers, json=burp0_json, timeout=10, proxies=proxies)
        if response.status_code != 200:
            return f"⚠️ Flipkart : API Blocked (HTTP {response.status_code})"
        try:
            jsonData = response.json()
        except ValueError:
            return "⚠️ Flipkart : Did not return JSON. IP might be temporarily blocked."
        response_block = jsonData.get('RESPONSE', {})
        user_details = response_block.get('userDetails', {})
        status = user_details.get(num_with_code)
        if status == "GUEST":
            return "❌ Not Registered (GUEST)"
        elif status == "VERIFIED":
            return "✅ Registered (VERIFIED)"
        elif status is None:
            return f"⚠️ Number not found in response."
        else:
            return f"ℹ️ Unknown Status ({status})"
    except Exception as e:
        return f"⚠️ Error: {type(e).__name__}: {str(e)}"

# ==================== INSTAGRAM DOWNLOADER ====================
L = instaloader.Instaloader(
    save_metadata=False,
    download_comments=False,
    post_metadata_txt_pattern=""
)

def download_reel(url):
    try:
        shortcode = re.search(r"/reel/(.*?)/", url).group(1)
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        L.download_post(post, target=shortcode)
        for file in os.listdir(shortcode):
            if file.endswith(".mp4"):
                return os.path.join(shortcode, file)
        return None
    except Exception as e:
        logger.error(f"Insta download error: {e}")
        return None

def download_bulk(urls):
    results = []
    for url in urls:
        path = download_reel(url)
        if path:
            results.append(path)
        time.sleep(1)
    return results

# ==================== APK ANALYSIS ====================
def get_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def extract_strings_from_dex_files(apk_path):
    all_strings = []
    try:
        with zipfile.ZipFile(apk_path, 'r') as apk_zip:
            for file_name in apk_zip.namelist():
                if file_name.endswith('.dex'):
                    dex_data = apk_zip.read(file_name)
                    current_string = ""
                    for byte in dex_data:
                        if 32 <= byte <= 126:
                            current_string += chr(byte)
                        else:
                            if len(current_string) >= 6:
                                all_strings.append(current_string)
                            current_string = ""
                    if len(current_string) >= 6:
                        all_strings.append(current_string)
    except Exception as e:
        logger.error(f"DEX extraction failed: {e}")
    return all_strings

def extract_from_manifest(apk_path):
    strings = []
    try:
        with zipfile.ZipFile(apk_path, 'r') as z:
            if 'AndroidManifest.xml' in z.namelist():
                manifest_data = z.read('AndroidManifest.xml')
                current_string = ""
                for byte in manifest_data:
                    if 32 <= byte <= 126:
                        current_string += chr(byte)
                    else:
                        if len(current_string) >= 4:
                            strings.append(current_string)
                        current_string = ""
                if len(current_string) >= 4:
                    strings.append(current_string)
    except Exception as e:
        logger.error(f"Manifest extraction failed: {e}")
    return strings

def get_package_info(apk_path):
    package_name = "Unknown"
    version_name = "Unknown"
    version_code = "Unknown"
    try:
        with zipfile.ZipFile(apk_path, 'r') as z:
            if 'AndroidManifest.xml' in z.namelist():
                manifest_data = z.read('AndroidManifest.xml')
                manifest_str = str(manifest_data)
                pkg_match = re.search(r'package=[\'"]([^\'"]+)[\'"]', manifest_str)
                if pkg_match:
                    package_name = pkg_match.group(1)
                version_match = re.search(r'versionName=[\'"]([^\'"]+)[\'"]', manifest_str)
                if version_match:
                    version_name = version_match.group(1)
                version_code_match = re.search(r'versionCode=[\'"]([^\'"]+)[\'"]', manifest_str)
                if version_code_match:
                    version_code = version_code_match.group(1)
    except Exception as e:
        logger.error(f"Package info extraction failed: {e}")
    return package_name, version_name, version_code

def search_in_strings(strings_list):
    found = {
        "firebase_urls": set(),
        "storage_urls": set(),
        "api_keys": set(),
        "secrets": set(),
        "json_endpoints": set()
    }
    firebase_pattern = r'(https?://[a-zA-Z0-9\-_]+\.(firebaseio\.com|firebasestorage\.app|firebaseapp\.com))'
    storage_pattern = r'([a-zA-Z0-9\-_]+\.(appspot\.com|googleapis\.com))'
    api_key_pattern = r'AIza[0-9A-Za-z\-_]{35}'
    secret_pattern = r'(?i)(secret|password|api_key|apikey|token|key|auth|authorization)\s*[=:]\s*["\']?([A-Za-z0-9+\/=]{20,})["\']?'
    json_pattern = r'(https?://[^\s<>"\'{}|\\^`\[\]]+\.json)'
    for s in strings_list:
        s_decoded = s if isinstance(s, str) else str(s)
        for match in re.findall(firebase_pattern, s_decoded, re.IGNORECASE):
            found["firebase_urls"].add(match[0])
        for match in re.findall(storage_pattern, s_decoded, re.IGNORECASE):
            found["storage_urls"].add(match)
        for match in re.findall(api_key_pattern, s_decoded):
            found["api_keys"].add(match)
        for match in re.findall(secret_pattern, s_decoded):
            if len(match[1]) > 16:
                found["secrets"].add(match[1])
        for match in re.findall(json_pattern, s_decoded, re.IGNORECASE):
            found["json_endpoints"].add(match)
    return found

def analyze_apk(apk_path):
    package_name, version_name, version_code = get_package_info(apk_path)
    manifest_strings = extract_from_manifest(apk_path)
    dex_strings = extract_strings_from_dex_files(apk_path)
    all_strings = manifest_strings + dex_strings
    creds = search_in_strings(all_strings)
    return {
        "package_name": package_name,
        "version_name": version_name,
        "version_code": version_code,
        "firebase_urls": list(creds["firebase_urls"]),
        "storage_urls": list(creds["storage_urls"]),
        "api_keys": list(creds["api_keys"]),
        "secrets": list(creds["secrets"]),
        "json_endpoints": list(creds["json_endpoints"])
    }, len(dex_strings)

def format_results(results, apk_path, file_size, num_dex_strings):
    md5_hash = get_md5(apk_path)
    file_size_mb = round(file_size / (1024 * 1024), 2)
    total = len(results["firebase_urls"]) + len(results["storage_urls"]) + len(results["api_keys"]) + len(results["secrets"]) + len(results["json_endpoints"])
    out = []
    out.append("╔══════════════════════════════════╗")
    out.append("║     🔓 EXTRACTED CREDENTIALS     ║")
    out.append("╚══════════════════════════════════╝")
    out.append("")
    out.append(f"📦 <code>{os.path.basename(apk_path)}</code>")
    out.append(f"📏 {file_size_mb} MB  🔒 {md5_hash[:16]}...")
    out.append("")
    if results["firebase_urls"]:
        out.append("🔥 <b>FIREBASE DATABASE:</b>")
        for url in results["firebase_urls"][:5]:
            out.append(f"   🌐 <code>{url}</code>")
            out.append(f"   📁 <code>{url}/.json</code>")
        out.append("")
    if results["storage_urls"]:
        out.append("📦 <b>STORAGE BUCKET:</b>")
        for storage in results["storage_urls"][:5]:
            out.append(f"   📦 <code>{storage}</code>")
        out.append("")
    if results["api_keys"]:
        out.append("🔑 <b>API KEYS:</b>")
        for key in results["api_keys"][:5]:
            out.append(f"   🔑 <code>{key}</code>")
        out.append("")
    if results["secrets"]:
        out.append("🔐 <b>SECRETS/TOKENS:</b>")
        for secret in results["secrets"][:5]:
            secret_display = secret[:40] + "..." if len(secret) > 40 else secret
            out.append(f"   🔐 <code>{secret_display}</code>")
        out.append("")
    if results["json_endpoints"]:
        out.append("📄 <b>JSON ENDPOINTS:</b>")
        for endpoint in results["json_endpoints"][:5]:
            out.append(f"   📄 <code>{endpoint}</code>")
        out.append("")
    if total == 0:
        out.append("⚠️ <i>No credentials found</i>")
        out.append(f"📊 Scanned {num_dex_strings} strings")
        out.append("💡 APK may be obfuscated")
    out.append("")
    out.append("📦 <b>Package:</b> <code>" + results["package_name"] + "</code>")
    out.append(f"🔢 <b>Version:</b> {results['version_name']} ({results['version_code']})")
    out.append("")
    out.append("⚠️ <i>DO NOT test without owner permission</i>")
    return "\n".join(out)

# ==================== INSTAGRAM VIEWER (FREE) ====================
IGVIEWER_API = "https://storyviewer.com/api/v1/web/profile"

def fetch_ig_data(username: str):
    try:
        response = requests.post(
            IGVIEWER_API,
            json={
                "username": username,
                "user_info": True,
                "user_stories": True,
                "user_highlights": True,
                "user_posts": True,
            },
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        logger.info(f"IG Viewer response keys: {list(data.keys())}")
        return data
    except Exception as e:
        logger.error(f"IG Viewer API failed: {e}")
        return None

def extract_media_ig(item: dict):
    media_url = item.get("source")
    if not media_url:
        for key in ["media_url", "url", "src", "link", "video", "image"]:
            if key in item and item[key]:
                media_url = item[key]
                break
    if not media_url:
        return None, None
    media_type = item.get("media_type", "image")
    if media_type not in ["video", "image"]:
        if media_url.lower().endswith((".mp4", ".mov", ".webm")):
            media_type = "video"
        else:
            media_type = "image"
    return media_url, media_type

def build_caption_ig(item: dict, prefix: str = ""):
    caption = prefix if prefix else ""
    mentions = item.get("mentions", [])
    if mentions:
        mention_str = ", ".join(f"@{m}" for m in mentions)
        if caption:
            caption += f"\n👥 Mentions: {mention_str}"
        else:
            caption = f"👥 Mentions: {mention_str}"
    taken_at = item.get("taken_at")
    if taken_at:
        if caption:
            caption += f"\n⏰ {taken_at}"
        else:
            caption = f"⏰ {taken_at}"
    return caption.strip()

def extract_lists_from_response(data: dict):
    lists = {}
    for key, value in data.items():
        if isinstance(value, list) and len(value) > 0:
            first = value[0]
            if isinstance(first, dict):
                if any(k in first for k in ['source', 'media_url', 'url', 'src', 'link']):
                    lists[key] = value
    return lists

def extract_user_info(data: dict):
    info_keys = ['user_info', 'user', 'profile', 'account']
    for key in info_keys:
        if key in data and isinstance(data[key], dict):
            return data[key]
    for key, value in data.items():
        if isinstance(value, dict):
            if 'username' in value or 'full_name' in value:
                return value
    return {}

# ==================== MUSIC API FUNCTIONS ====================
MUSIC_API_BASE = "https://jiosavanapiryden.vercel.app/api"

def search_songs(query, page=0, limit=15):
    try:
        url = f"{MUSIC_API_BASE}/search/songs"
        params = {"query": query, "page": page, "limit": limit}
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        logger.error(f"Music search error: {e}")
        return None

def get_song_details(song_id):
    try:
        url = f"{MUSIC_API_BASE}/songs/{song_id}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("data"):
                song_info = data["data"][0]
                download_links = song_info.get("downloadUrl", [])
                if download_links:
                    best = download_links[-1]
                    dur = song_info.get("duration", 0)
                    minutes = dur // 60
                    seconds = dur % 60
                    return {
                        "url": best.get("url"),
                        "title": song_info.get("name", "Unknown"),
                        "artist": ", ".join([a.get("name", "") for a in song_info.get("artists", {}).get("primary", [])]),
                        "duration": dur,
                        "duration_formatted": f"{minutes}:{seconds:02d}",
                        "album": song_info.get("album", {}).get("name", ""),
                        "year": song_info.get("year", "N/A")
                    }
        return None
    except Exception as e:
        logger.error(f"Song details error: {e}")
        return None

def format_duration(seconds):
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes}:{remaining_seconds:02d}"

# ==================== HANDLERS ====================

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user = message.from_user
    user_id = user.id
    username = user.username or "NoUsername"
    first_name = user.first_name or "User"
    
    args = message.text.split()
    referred_by = None
    if len(args) > 1 and args[1].startswith('ref_'):
        try:
            referred_by = int(args[1].split('_')[1])
        except:
            pass
    
    existing = get_user(user_id)
    if not existing:
        create_user(user_id, username, first_name, referred_by)
    
    if not check_membership(user_id):
        text = (
            f"🔐 <b>Access Denied</b> 😞!\n\n"
            f"You must join our channel to use this bot.\n\n"
            f"📢 <b>Required Channel:</b>\n"
            f"• Channel: <a href='https://t.me/{CHANNEL_USERNAME}'>{CHANNEL_USERNAME}</a>\n\n"
            f"⚠️ After joining, click <b>VERIFY</b> button."
        )
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME}"))
        keyboard.add(InlineKeyboardButton("✅ VERIFY MEMBERSHIP ✅", callback_data="verify_membership", style="success"))
        bot.send_message(message.chat.id, text, reply_markup=keyboard, parse_mode="HTML", disable_web_page_preview=True)
        return
    
    balance = get_user_balance(user_id)
    is_admin = (user_id == ADMIN_ID)
    text = main_menu_text(user_id, first_name, balance, "ACTIVE")
    bot.send_message(message.chat.id, text, reply_markup=main_menu_keyboard(is_admin), parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == "verify_membership")
def verify_membership_callback(call):
    user_id = call.from_user.id
    if check_membership(user_id):
        bot.answer_callback_query(call.id, "✅ Verified! You can now use the bot.")
        user = call.from_user
        balance = get_user_balance(user_id)
        is_admin = (user_id == ADMIN_ID)
        text = main_menu_text(user_id, user.first_name, balance, "ACTIVE")
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=main_menu_keyboard(is_admin), parse_mode="HTML")
    else:
        bot.answer_callback_query(call.id, "❌ Please join the channel first!", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith("module_"))
def handle_module_callback(call):
    module = call.data.split("_")[1]
    user_id = call.from_user.id
    balance = get_user_balance(user_id)

    if module not in ["referral", "admin", "music", "igviewer", "shopsy", "yoga"]:
        if not check_membership(user_id):
            bot.answer_callback_query(call.id, "❌ Please join channel first!", show_alert=True)
            return

    if module == "firebase":
        user_firebase_state[user_id] = False
        bot.delete_message(call.message.chat.id, call.message.message_id)
        text = firebase_menu_text(user_id, balance, "ACTIVE", get_module_cost("firebase"))
        bot.send_message(call.message.chat.id, text, reply_markup=firebase_menu_keyboard(), parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif module == "temp":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        text = temp_menu_text(user_id)
        bot.send_message(call.message.chat.id, text, reply_markup=temp_menu_keyboard(), parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif module == "flipkart":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        text = flipkart_menu_text(user_id, balance, "ACTIVE", get_module_cost("flipkart"))
        bot.send_message(call.message.chat.id, text, reply_markup=flipkart_menu_keyboard(), parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif module == "instagram":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        text = instagram_menu_text(user_id, balance, "ACTIVE", get_module_cost("instagram_single"))
        bot.send_message(call.message.chat.id, text, reply_markup=instagram_menu_keyboard(), parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif module == "referral":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        referral_count = get_referral_count(user_id)
        text = referral_menu_text(user_id, balance, referral_count)
        bot.send_message(call.message.chat.id, text, reply_markup=referral_menu_keyboard(), parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif module == "music":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        user_music_state[user_id] = "waiting_for_search"
        text = (
            "🎵 <b>MUSIC DOWNLOADER</b>\n\n"
            "Send me a song name or artist name.\n"
            "I'll search and provide high-quality audio (320kbps).\n\n"
            "💡 Cost: FREE – unlimited downloads!\n"
            "📝 Example: <i>Believer</i> or <i>Arijit Singh</i>\n\n"
            "Send <code>/cancel</code> to cancel."
        )
        bot.send_message(call.message.chat.id, text, parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif module == "admin":
        if call.from_user.id != ADMIN_ID:
            bot.answer_callback_query(call.id, "⛔ Admin only!")
            return
        bot.delete_message(call.message.chat.id, call.message.message_id)
        text = admin_panel_text()
        bot.send_message(call.message.chat.id, text, reply_markup=admin_panel_keyboard(), parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif module == "igviewer":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        user_igviewer_state[user_id] = "waiting_username"
        bot.send_message(
            call.message.chat.id,
            "👁️ <b>Instagram Viewer</b>\n\n"
            "Send me an Instagram username (without @).\n"
            "Example: <code>realmadrid</code>\n\n"
            "⚡ <b>Free & Unlimited</b> – no credits needed!",
            parse_mode="HTML"
        )
        bot.answer_callback_query(call.id)

    elif module == "shopsy":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        shopsy_bal = get_shopsy_balance(user_id)
        shopsy_logged_in = get_shopsy_login_status(user_id)
        text = shopsy_menu_text(user_id, balance, "ACTIVE", shopsy_bal, shopsy_logged_in)
        bot.send_message(call.message.chat.id, text, reply_markup=shopsy_menu_keyboard(), parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif module == "yoga":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('SELECT yoga_code FROM users WHERE user_id = ?', (user_id,))
        row = c.fetchone()
        conn.close()
        yoga_code = row[0] if row else None
        
        balance = get_user_balance(user_id)
        text = yoga_menu_text(user_id, balance, "ACTIVE", yoga_code, get_yoga_refer_reward(), get_module_cost("yoga"))
        bot.send_message(call.message.chat.id, text, reply_markup=yoga_menu_keyboard(), parse_mode="HTML")
        bot.answer_callback_query(call.id)

# ==================== Referral callbacks ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith("referral_"))
def handle_referral_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    msg_id = call.message.message_id

    if call.data == "referral_get_link":
        if not check_membership(user_id):
            bot.answer_callback_query(call.id, "❌ Please join channel first!", show_alert=True)
            return
        link = get_referral_link(user_id)
        bot.answer_callback_query(call.id, "🔗 Link copied! Share it with friends.")
        bot.edit_message_text(
            f"🔗 <b>Your Referral Link</b>\n\n<code>{link}</code>\n\n"
            f"📤 Share this link with your friends!\n"
            f"🎁 You get <b>+{REFERRAL_BONUS} Credits</b> per referral (after 24h).\n"
            f"🎁 Your friend gets <b>+{NEW_USER_BONUS} Credits</b> on joining.\n\n"
            f"⚠️ Make sure your friend joins the channel!",
            chat_id=chat_id, message_id=msg_id,
            reply_markup=referral_menu_keyboard(), parse_mode="HTML"
        )

    elif call.data == "referral_stats":
        referral_count = get_referral_count(user_id)
        pending_count = get_pending_referral_count(user_id)
        bot.answer_callback_query(call.id, "📊 Fetching your stats...")
        bot.edit_message_text(
            f"📊 <b>Your Referral Stats</b>\n\n"
            f"👥 Confirmed Referrals: <b>{referral_count}</b>\n"
            f"⏳ Pending (24h): <b>{pending_count}</b>\n"
            f"💰 Bonus per referral: <b>+{REFERRAL_BONUS} Credits</b>\n"
            f"🎁 New user bonus: <b>+{NEW_USER_BONUS} Credits</b>\n\n"
            f"💡 Referrals are confirmed after 24 hours of stay in our community.",
            chat_id=chat_id, message_id=msg_id,
            reply_markup=referral_menu_keyboard(), parse_mode="HTML"
        )

# ==================== Firebase callbacks ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith("firebase_"))
def handle_firebase_callback(call):
    action = call.data.split("_")[1]
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    msg_id = call.message.message_id
    balance = get_user_balance(user_id)
    cost = get_module_cost("firebase")

    if action == "send":
        if balance < cost:
            bot.answer_callback_query(call.id, f"❌ You need {cost} credits for Firebase analysis.", show_alert=True)
            return
        user_firebase_state[user_id] = True
        bot.answer_callback_query(call.id, "📤 Ready! Send your APK file.")
        bot.edit_message_text(
            f"📤 <b>Send APK</b>\n\n"
            f"Please upload your APK file.\n"
            f"I will analyze it for Firebase credentials and other sensitive data.\n\n"
            f"⏱️ Analysis may take 30-60 seconds.\n"
            f"💰 Cost: {cost} Credits.\n"
            f"Click <b>Remove APK</b> to cancel.",
            chat_id=chat_id,
            message_id=msg_id,
            reply_markup=firebase_menu_keyboard(),
            parse_mode="HTML"
        )

    elif action == "remove":
        user_firebase_state[user_id] = False
        bot.answer_callback_query(call.id, "🗑️ Firebase session cleared.")
        bot.edit_message_text(
            "🗑️ <b>APK Removed</b>\n\n"
            "Any pending APK upload has been cleared.\n"
            "You can send a new APK anytime.",
            chat_id=chat_id,
            message_id=msg_id,
            reply_markup=firebase_menu_keyboard(),
            parse_mode="HTML"
        )

# ==================== APK handler ====================
@bot.message_handler(content_types=['document'])
def handle_apk(message):
    user_id = message.from_user.id
    if not user_firebase_state.get(user_id, False):
        bot.reply_to(message, "❌ Please click <b>Send APK</b> in the Firebase Extractor module first.", parse_mode="HTML")
        return

    doc = message.document
    if not doc.file_name or not doc.file_name.lower().endswith(".apk"):
        bot.reply_to(message, "❌ Please send an <code>.apk</code> file.", parse_mode="HTML")
        return

    if doc.file_size > 50 * 1024 * 1024:
        bot.reply_to(message, "❌ Max file size: 50 MB.")
        return

    cost = get_module_cost("firebase")
    balance = get_user_balance(user_id)
    if balance < cost:
        bot.reply_to(message, f"❌ Insufficient credits! You need {cost} credits. Your balance: {balance}")
        return

    # Deduct credits (will be refunded on failure)
    update_user_balance(user_id, -cost)
    processing_msg = bot.reply_to(message, "⏳ Analyzing APK... (may take 30-60 seconds)")

    tmp_path = None
    try:
        file_info = bot.get_file(doc.file_id)
        tmp_path = f"/tmp/{doc.file_name}"
        downloaded_file = bot.download_file(file_info.file_path)
        with open(tmp_path, "wb") as f:
            f.write(downloaded_file)
        file_size = doc.file_size

        results, num_dex_strings = analyze_apk(tmp_path)
        reply = format_results(results, tmp_path, file_size, num_dex_strings)
        if len(reply) > 4096:
            reply = reply[:4000] + "\n\n...(truncated)"
        bot.edit_message_text(reply, chat_id=message.chat.id, message_id=processing_msg.message_id, parse_mode="HTML")
        log_usage(user_id, "Firebase Extractor", f"APK: {doc.file_name}")
    except Exception as e:
        logger.error(f"APK analysis error: {e}")
        update_user_balance(user_id, cost)  # REFUND
        bot.edit_message_text(
            f"❌ Analysis failed!\n\nError: {str(e)[:200]}\n\nCredits refunded.",
            chat_id=message.chat.id,
            message_id=processing_msg.message_id,
            parse_mode="HTML"
        )
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except:
                pass

# ==================== INSTAGRAM VIEWER HANDLERS ====================
@bot.message_handler(func=lambda message: user_igviewer_state.get(message.from_user.id) == "waiting_username")
def igviewer_username_handler(message):
    user_id = message.from_user.id
    username = message.text.strip().lstrip('@')
    if not username or len(username) < 2:
        bot.reply_to(message, "❌ Please enter a valid username (at least 2 characters).")
        return

    processing = bot.reply_to(message, f"🔍 Fetching data for <b>@{username}</b>...", parse_mode="HTML")
    data = fetch_ig_data(username)
    if not data:
        bot.edit_message_text("❌ Failed to fetch profile. Please try again later.", chat_id=message.chat.id, message_id=processing.message_id)
        user_igviewer_state[user_id] = None
        return

    lists = extract_lists_from_response(data)
    if not lists:
        bot.edit_message_text("❌ No media found for this user.", chat_id=message.chat.id, message_id=processing.message_id)
        user_igviewer_state[user_id] = None
        return

    user_info = extract_user_info(data)
    igviewer_data[user_id] = {
        "username": username,
        "data": data,
        "lists": lists,
        "current_list_key": None,
        "current_page": 0,
        "sent_media_ids": []
    }
    user_igviewer_state[user_id] = None

    buttons = []
    list_names = {
        'stories': '📸 Stories',
        'highlights': '⭐ Highlights',
        'posts': '📷 Posts',
        'user_stories': '📸 Stories',
        'user_highlights': '⭐ Highlights',
        'user_posts': '📷 Posts',
    }
    for key in lists.keys():
        label = list_names.get(key, key.title())
        buttons.append([InlineKeyboardButton(label, callback_data=f"igviewer_list_{key}")])
    if user_info:
        buttons.append([InlineKeyboardButton("ℹ️ Info", callback_data="igviewer_info")])
    buttons.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu")])

    reply_markup = InlineKeyboardMarkup(buttons)
    bot.edit_message_text(
        f"📱 <b>@{username}</b> – choose what to view:",
        chat_id=message.chat.id,
        message_id=processing.message_id,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("igviewer_"))
def igviewer_callback(call):
    user_id = call.from_user.id
    action = call.data.split("_", 1)[1]

    data = igviewer_data.get(user_id)
    if not data:
        bot.answer_callback_query(call.id, "Session expired.")
        return

    if action == "info":
        user_info = extract_user_info(data["data"])
        if not user_info:
            bot.answer_callback_query(call.id, "No profile info available.")
            return
        text = (
            f"<b>👤 Profile Info</b>\n\n"
            f"Username: @{user_info.get('username', 'N/A')}\n"
            f"Full Name: {user_info.get('full_name', 'N/A')}\n"
            f"Bio: {user_info.get('bio', 'N/A')}\n"
            f"Followers: {user_info.get('follower_count', 0)}\n"
            f"Following: {user_info.get('following_count', 0)}\n"
            f"Posts: {user_info.get('media_count', 0)}"
        )
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="igviewer_back")]]
        bot.edit_message_text(
            text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )
        bot.answer_callback_query(call.id)
        return

    if action == "back":
        lists = data.get("lists", {})
        user_info = extract_user_info(data["data"])
        buttons = []
        list_names = {
            'stories': '📸 Stories',
            'highlights': '⭐ Highlights',
            'posts': '📷 Posts',
            'user_stories': '📸 Stories',
            'user_highlights': '⭐ Highlights',
            'user_posts': '📷 Posts',
        }
        for key in lists.keys():
            label = list_names.get(key, key.title())
            buttons.append([InlineKeyboardButton(label, callback_data=f"igviewer_list_{key}")])
        if user_info:
            buttons.append([InlineKeyboardButton("ℹ️ Info", callback_data="igviewer_info")])
        buttons.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu")])
        reply_markup = InlineKeyboardMarkup(buttons)
        bot.edit_message_text(
            f"📱 <b>@{data['username']}</b> – choose what to view:",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
        data["sent_media_ids"] = []
        igviewer_data[user_id] = data
        bot.answer_callback_query(call.id)
        return

    if action.startswith("list_"):
        list_key = action.split("_", 1)[1]
        items = data["lists"].get(list_key, [])
        if not items:
            bot.answer_callback_query(call.id, "No items in this list.")
            return
        data["current_list_key"] = list_key
        data["current_list"] = items
        data["current_page"] = 0
        igviewer_data[user_id] = data
        send_igviewer_page(call.message.chat.id, user_id, call.message.message_id)
        bot.answer_callback_query(call.id)
        return

    if action in ["prev", "next"]:
        if action == "next":
            data["current_page"] = data.get("current_page", 0) + 1
        elif action == "prev":
            data["current_page"] = max(0, data.get("current_page", 0) - 1)
        igviewer_data[user_id] = data
        send_igviewer_page(call.message.chat.id, user_id, call.message.message_id)
        bot.answer_callback_query(call.id)
        return

def send_igviewer_page(chat_id, user_id, edit_msg_id=None):
    data = igviewer_data.get(user_id)
    if not data:
        return
    items = data["current_list"]
    page = data["current_page"]
    items_per_page = 3
    total = len(items)
    start = page * items_per_page
    end = min(start + items_per_page, total)
    if start >= total:
        page = (total - 1) // items_per_page
        start = page * items_per_page
        end = min(start + items_per_page, total)
        data["current_page"] = page
        igviewer_data[user_id] = data

    page_items = items[start:end]
    sent_ids = data.get("sent_media_ids", [])
    for mid in sent_ids:
        try:
            bot.delete_message(chat_id, mid)
        except:
            pass
    new_sent_ids = []

    for item in page_items:
        media_url, media_type = extract_media_ig(item)
        if not media_url:
            continue
        caption = build_caption_ig(item)
        try:
            if media_type == "video":
                msg = bot.send_video(chat_id, media_url, caption=caption)
            else:
                msg = bot.send_photo(chat_id, media_url, caption=caption)
            new_sent_ids.append(msg.message_id)
        except Exception as e:
            logger.error(f"IG Viewer send failed: {e}")
            try:
                resp = requests.get(media_url, timeout=20)
                resp.raise_for_status()
                if media_type == "video":
                    msg = bot.send_video(chat_id, resp.content, caption=caption)
                else:
                    msg = bot.send_photo(chat_id, resp.content, caption=caption)
                new_sent_ids.append(msg.message_id)
            except Exception as e2:
                logger.error(f"Fallback failed: {e2}")

    data["sent_media_ids"] = new_sent_ids
    igviewer_data[user_id] = data

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Prev", callback_data="igviewer_prev"))
    if end < total:
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data="igviewer_next"))
    nav_buttons.append(InlineKeyboardButton("🔙 Back", callback_data="igviewer_back"))
    nav_markup = InlineKeyboardMarkup([nav_buttons] if nav_buttons else [])

    list_key = data.get("current_list_key", "")
    label_map = {
        'stories': '📸 Stories',
        'highlights': '⭐ Highlights',
        'posts': '📷 Posts',
        'user_stories': '📸 Stories',
        'user_highlights': '⭐ Highlights',
        'user_posts': '📷 Posts',
    }
    label = label_map.get(list_key, list_key.title())
    hub_text = f"📄 <b>{label}</b> – Page {page+1}/{(total + items_per_page - 1)//items_per_page}\n\n(Showing {len(page_items)} items)"

    if edit_msg_id:
        bot.edit_message_text(hub_text, chat_id=chat_id, message_id=edit_msg_id, reply_markup=nav_markup, parse_mode="HTML")

# ==================== Temp Mail callbacks ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith("temp_"))
def handle_temp_callback(call):
    action = call.data.split("_")[1]
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    msg_id = call.message.message_id

    if action == "new":
        if user_id in user_temp_sessions:
            user_temp_sessions[user_id] = None
        temp = TempMailBot()
        result = temp.generate_email()
        if result['success']:
            user_temp_sessions[user_id] = temp
            bot.answer_callback_query(call.id, "✅ New email created!")
            bot.edit_message_text(
                f"📧 <b>New Email Created!</b>\n\n"
                f"📧 <b>Email:</b> <code>{result['email']}</code>\n"
                f"⏱️ <b>Expires:</b> 10 minutes\n\n"
                f"💡 Use <b>Check Inbox</b> to see messages\n"
                f"🔑 Use <b>Get OTP</b> to auto-detect OTP\n\n"
                f"<i>Powered By Viediet Utility</i>",
                chat_id=chat_id,
                message_id=msg_id,
                reply_markup=temp_menu_keyboard(),
                parse_mode="HTML"
            )
        else:
            bot.answer_callback_query(call.id, "❌ Failed to create email!", show_alert=True)
            bot.edit_message_text(
                f"❌ <b>Failed!</b>\n\nError: {result.get('error', 'Unknown')}",
                chat_id=chat_id,
                message_id=msg_id,
                reply_markup=temp_menu_keyboard(),
                parse_mode="HTML"
            )

    elif action == "inbox":
        if user_id not in user_temp_sessions:
            bot.answer_callback_query(call.id, "❌ No email! Create one first.", show_alert=True)
            return
        temp = user_temp_sessions[user_id]
        if temp.expiry_time and datetime.now() > temp.expiry_time:
            bot.answer_callback_query(call.id, "❌ Email expired! Create new one.", show_alert=True)
            del user_temp_sessions[user_id]
            return
        bot.answer_callback_query(call.id, "📥 Checking inbox...")
        messages = temp.check_inbox()
        if not messages:
            bot.edit_message_text(
                "📥 <b>Inbox</b>\n\n📭 No messages yet!\n\n💡 Try getting OTP.",
                chat_id=chat_id,
                message_id=msg_id,
                reply_markup=temp_menu_keyboard(),
                parse_mode="HTML"
            )
            return
        inbox_text = f"📥 <b>Inbox</b>\n\n"
        for i, msg in enumerate(messages[-5:], 1):
            from_addr = msg.get('from', {}).get('address', 'Unknown')
            subject = msg.get('subject', 'No Subject')
            inbox_text += f"━━━━━━━━━━━━━━━━━━━━\n"
            inbox_text += f"{i}. 📧 <b>From:</b> {from_addr}\n"
            inbox_text += f"   📝 <b>Subject:</b> {subject}\n"
            body = msg.get('body', '')
            if not body:
                full = temp.get_message_content(msg['id'])
                if full:
                    body = full.get('text', '')
            combined = body + " " + subject
            otp_match = re.search(r'\b\d{4,6}\b', combined)
            if otp_match:
                inbox_text += f"   🔑 <b>OTP:</b> <code>{otp_match.group()}</code>\n"
            inbox_text += f"\n"
        inbox_text += f"━━━━━━━━━━━━━━━━━━━━\n"
        inbox_text += f"📊 <b>Total:</b> {len(messages)} messages\n\n"
        inbox_text += f"<i>Powered By Viediet Utility</i>"
        bot.edit_message_text(
            inbox_text,
            chat_id=chat_id,
            message_id=msg_id,
            reply_markup=temp_menu_keyboard(),
            parse_mode="HTML"
        )

    elif action == "otp":
        if user_id not in user_temp_sessions:
            bot.answer_callback_query(call.id, "❌ No email! Create one first.", show_alert=True)
            return
        temp = user_temp_sessions[user_id]
        if temp.expiry_time and datetime.now() > temp.expiry_time:
            bot.answer_callback_query(call.id, "❌ Email expired! Create new one.", show_alert=True)
            del user_temp_sessions[user_id]
            return
        bot.answer_callback_query(call.id, "🔑 Monitoring for OTP...")
        waiting_msg = bot.send_message(
            chat_id,
            "🔑 <b>Waiting for OTP...</b>\n\n"
            "⏳ Monitoring inbox...\n"
            "📩 OTP will appear here instantly\n"
            "⏱️ Timeout: 2 minutes\n\n"
            "<i>Powered By Viediet Utility</i>",
            parse_mode='HTML'
        )
        def otp_callback(result):
            if result:
                from_display = result['from_name'] if result['from_name'] else result['from']
                bot.edit_message_text(
                    f"🔑 <b>✅ OTP Received!</b>\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔑 <b>OTP Code:</b> <code>{result['otp']}</code>\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📧 <b>From:</b> {from_display}\n"
                    f"📧 <b>Email:</b> {result['from']}\n"
                    f"📝 <b>Subject:</b> {result['subject']}\n"
                    f"⏱️ <b>Time:</b> {result['time']}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"<i>Powered By Viediet Utility</i>",
                    chat_id=chat_id,
                    message_id=waiting_msg.message_id,
                    parse_mode='HTML'
                )
            else:
                bot.edit_message_text(
                    "❌ <b>No OTP Found!</b>\n\n"
                    "⏱️ No OTP received in 2 minutes.\n\n"
                    "💡 <b>Try:</b>\n"
                    "• Send OTP again\n"
                    "• Check inbox manually\n"
                    "• Create new email\n\n"
                    "<i>Powered By Viediet Utility</i>",
                    chat_id=chat_id,
                    message_id=waiting_msg.message_id,
                    parse_mode='HTML'
                )
        thread = threading.Thread(target=temp.wait_for_otp, args=(otp_callback, 120))
        thread.daemon = True
        thread.start()

    elif action == "delete":
        if user_id in user_temp_sessions:
            user_temp_sessions[user_id] = None
            del user_temp_sessions[user_id]
        bot.answer_callback_query(call.id, "✅ Email deleted!")
        bot.edit_message_text(
            "🗑️ <b>Email Deleted</b>\n\n"
            "Your temporary email has been deleted.\n\n"
            "<i>Powered By Viediet Utility</i>",
            chat_id=chat_id,
            message_id=msg_id,
            reply_markup=temp_menu_keyboard(),
            parse_mode="HTML"
        )

# ==================== Flipkart checker callback ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith("flipkart_"))
def handle_flipkart_callback(call):
    bot.answer_callback_query(call.id, "📱 Send a 10-digit number to check.")

# ---------- Phone number handler (Flipkart) ----------
@bot.message_handler(func=lambda message: message.text and message.text.isdigit() and len(message.text) == 10)
def handle_phone_number(message):
    user_id = message.from_user.id

    if (user_firebase_state.get(user_id) or 
        user_music_state.get(user_id) or
        user_igviewer_state.get(user_id) or
        user_shopsy_state.get(user_id) or
        user_yoga_state.get(user_id)):
        return

    cost = get_module_cost("flipkart")
    balance = get_user_balance(user_id)
    if balance < cost:
        bot.reply_to(message, f"❌ Insufficient credits! You need {cost} credit to check a number.")
        return
    
    # Deduct credits (will be refunded on failure)
    update_user_balance(user_id, -cost)
    processing = bot.reply_to(message, f"🔍 Checking <code>{message.text}</code> on Flipkart...", parse_mode="HTML")
    
    def check_thread():
        try:
            result = check_flipkart(message.text)
            new_balance = get_user_balance(user_id)
            bot.edit_message_text(
                f"📱 <b>Result for {message.text}</b>\n\n{result}\n\n💰 Remaining Credits: {new_balance}",
                chat_id=message.chat.id,
                message_id=processing.message_id,
                parse_mode="HTML"
            )
            log_usage(user_id, "Flipkart Checker", f"Number: {message.text}")
        except Exception as e:
            update_user_balance(user_id, cost)  # REFUND
            bot.edit_message_text(
                f"❌ Error: {str(e)[:200]}\n\nCredits refunded.",
                chat_id=message.chat.id,
                message_id=processing.message_id,
                parse_mode="HTML"
            )
    threading.Thread(target=check_thread).start()

# ==================== Instagram callbacks (Downloader) ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith("instagram_"))
def handle_instagram_callback(call):
    action = call.data.split("_")[1]
    user_id = call.from_user.id
    cost = get_module_cost("instagram_single")

    if action == "single":
        balance = get_user_balance(user_id)
        if balance < cost:
            bot.answer_callback_query(call.id, f"❌ You need {cost} credit for download.", show_alert=True)
            return
        user_instagram_state[user_id] = "single"
        bot.answer_callback_query(call.id, "📹 Send a single Instagram video URL.")
        bot.edit_message_text(
            f"📹 <b>Single Download</b>\n\n"
            f"Send me the Instagram video link.\n"
            f"Example: <code>https://www.instagram.com/reel/xyz123/</code>\n\n"
            f"💡 Costs {cost} Credit.\n\n"
            f"<i>Powered By Viediet Utility</i>",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=instagram_menu_keyboard(),
            parse_mode="HTML"
        )

    elif action == "bulk":
        user_instagram_state[user_id] = "bulk"
        bot.answer_callback_query(call.id, "📚 Send multiple Instagram video URLs (one per line).")
        bot.edit_message_text(
            "📚 <b>Bulk Download</b>\n\n"
            "Send me multiple Instagram video links,\n"
            "each on a new line.\n\n"
            "Example:\n"
            "<code>https://www.instagram.com/reel/abc/\n"
            "https://www.instagram.com/reel/def/</code>\n\n"
            f"💡 Costs {cost} Credit per video.\n\n"
            f"<i>Powered By Viediet Utility</i>",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=instagram_menu_keyboard(),
            parse_mode="HTML"
        )

@bot.message_handler(func=lambda message: message.text and 'instagram.com' in message.text.lower())
def handle_instagram_link(message):
    user_id = message.from_user.id
    balance = get_user_balance(user_id)
    state = user_instagram_state.get(user_id)
    cost = get_module_cost("instagram_single")

    if not state:
        bot.reply_to(message, "📥 Please use the Instagram Downloader module from the main menu to send links.")
        return

    lines = message.text.strip().splitlines()
    urls = [line.strip() for line in lines if 'instagram.com' in line]

    if not urls:
        bot.reply_to(message, "❌ No valid Instagram URLs found.")
        return

    if state == "single":
        if balance < cost:
            bot.reply_to(message, f"❌ Insufficient credits! You need {cost} credit to download.")
            return
        # Deduct credits (will be refunded on failure)
        update_user_balance(user_id, -cost)
        processing = bot.reply_to(message, "⏳ Downloading reel...")
        
        def download_single():
            try:
                file_path = download_reel(urls[0])
                if file_path:
                    try:
                        with open(file_path, "rb") as vid:
                            bot.send_video(message.chat.id, vid, caption="✅ Downloaded successfully!")
                        os.remove(file_path)
                        shutil.rmtree(os.path.dirname(file_path), ignore_errors=True)
                    except Exception as e:
                        bot.send_message(message.chat.id, f"❌ Upload failed: {e}")
                        update_user_balance(user_id, cost)  # REFUND
                else:
                    bot.send_message(message.chat.id, "❌ Failed to download reel. Check URL or try again.")
                    update_user_balance(user_id, cost)  # REFUND
                bot.delete_message(message.chat.id, processing.message_id)
            except Exception as e:
                update_user_balance(user_id, cost)  # REFUND
                bot.send_message(message.chat.id, f"❌ Error: {str(e)[:200]}\n\nCredits refunded.")
        threading.Thread(target=download_single).start()

    elif state == "bulk":
        total_cost = len(urls) * cost
        if balance < total_cost:
            bot.reply_to(message, f"❌ Insufficient credits! Need {total_cost} credits for {len(urls)} videos.")
            return
        # Deduct credits (will be refunded on failure)
        update_user_balance(user_id, -total_cost)
        processing = bot.reply_to(message, f"⏳ Downloading {len(urls)} reels...")
        
        def download_bulk_thread():
            try:
                paths = download_bulk(urls)
                if paths:
                    for path in paths:
                        try:
                            with open(path, "rb") as vid:
                                bot.send_video(message.chat.id, vid)
                            os.remove(path)
                            shutil.rmtree(os.path.dirname(path), ignore_errors=True)
                        except Exception as e:
                            bot.send_message(message.chat.id, f"❌ Upload failed for one video: {e}")
                    bot.send_message(message.chat.id, f"✅ All {len(paths)} videos sent successfully!")
                else:
                    bot.send_message(message.chat.id, "❌ Failed to download any reel.")
                    update_user_balance(user_id, total_cost)  # REFUND
                bot.delete_message(message.chat.id, processing.message_id)
            except Exception as e:
                update_user_balance(user_id, total_cost)  # REFUND
                bot.send_message(message.chat.id, f"❌ Error: {str(e)[:200]}\n\nCredits refunded.")
        threading.Thread(target=download_bulk_thread).start()

    user_instagram_state[user_id] = None

# ==================== Admin callbacks ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
def handle_admin_callback(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "⛔ Admin only!")
        return
    chat_id = call.message.chat.id
    msg_id = call.message.message_id

    if call.data == "admin_stats":
        total_users = get_total_users()
        total_coins = get_total_coins()
        total_usage = get_total_usage()
        bot.edit_message_text(
            f"📊 <b>Bot Statistics</b>\n\n"
            f"👥 Total Users: <b>{total_users}</b>\n"
            f"💰 Total Coins: <b>{total_coins}</b>\n"
            f"📈 Total Usage: <b>{total_usage}</b> operations\n"
            f"🔢 Admin ID: <code>{ADMIN_ID}</code>",
            chat_id=chat_id, message_id=msg_id,
            reply_markup=admin_panel_keyboard(),
            parse_mode="HTML"
        )
        bot.answer_callback_query(call.id)

    elif call.data == "admin_users":
        users = get_all_users()
        if not users:
            msg = "No users found."
        else:
            msg = "👥 <b>User List (Top 20 by coins)</b>\n\n"
            for i, (uid, uname, bal, stat) in enumerate(users[:20], 1):
                msg += f"{i}. <code>{uname}</code> (ID: {uid}) – {bal} coins [{stat}]\n"
        bot.edit_message_text(msg, chat_id=chat_id, message_id=msg_id,
                              reply_markup=admin_panel_keyboard(), parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif call.data == "admin_add_coins":
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            "➕ <b>Add Coins</b>\n\nSend message in format:\n`/addcoins @username amount`\nor\n`/addcoins user_id amount`\n\nExample: `/addcoins @Viediet 50`",
            chat_id=chat_id, message_id=msg_id,
            reply_markup=admin_panel_keyboard(), parse_mode="HTML"
        )

    elif call.data == "admin_remove_coins":
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            "➖ <b>Remove Coins</b>\n\nSend message in format:\n`/removecoins @username amount`\nor\n`/removecoins user_id amount`\n\nExample: `/removecoins @Viediet 20`",
            chat_id=chat_id, message_id=msg_id,
            reply_markup=admin_panel_keyboard(), parse_mode="HTML"
        )

    elif call.data == "admin_broadcast":
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            "📢 <b>Broadcast</b>\n\nSend a message to all users.\nFormat: `/broadcast your message here`\n\nExample: `/broadcast Hello everyone!`",
            chat_id=chat_id, message_id=msg_id,
            reply_markup=admin_panel_keyboard(), parse_mode="HTML"
        )

    elif call.data == "admin_costs":
        current_costs = "\n".join([f"• {k}: {get_module_cost(k)} credits" for k in DEFAULT_COSTS.keys()])
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            f"⚙️ <b>Current Costs</b>\n\n{current_costs}\n\n"
            f"To change, send:\n`/setcost module amount`\n\n"
            f"Available modules: {', '.join(DEFAULT_COSTS.keys())}",
            chat_id=chat_id, message_id=msg_id,
            reply_markup=admin_panel_keyboard(), parse_mode="HTML"
        )

# ---------- Music Handlers (UNLIMITED) ----------
@bot.message_handler(func=lambda message: user_music_state.get(message.from_user.id) == "waiting_for_search")
def handle_music_search(message):
    user_id = message.from_user.id
    query = message.text.strip()
    
    if query.lower() == '/cancel':
        user_music_state[user_id] = None
        bot.reply_to(message, "❌ Search cancelled.", reply_markup=main_menu_keyboard(is_admin=(user_id==ADMIN_ID)))
        return
    
    if len(query) < 2:
        bot.reply_to(message, "❌ Please enter at least 2 characters.")
        return
    
    searching_msg = bot.reply_to(message, f"🎵 Searching for <b>{query}</b>...\n\n⏳ Please wait.")
    
    results = search_songs(query, page=0, limit=15)
    if not results or not results.get("success"):
        bot.edit_message_text("❌ No results found. Try different spelling.", chat_id=message.chat.id, message_id=searching_msg.message_id)
        return
    
    songs = results.get("data", {}).get("results", [])
    if not songs:
        bot.edit_message_text("❌ No songs found for that query.", chat_id=message.chat.id, message_id=searching_msg.message_id)
        return
    
    keyboard = InlineKeyboardMarkup(row_width=1)
    for idx, song in enumerate(songs[:15], 1):
        title = song.get("name", "Unknown")
        artists = song.get("artists", {}).get("primary", [])
        artist_names = ", ".join([a.get("name", "") for a in artists[:2]])
        duration = song.get("duration", 0)
        dur_str = format_duration(duration)
        button_text = f"{idx}. {title[:30]} - {artist_names[:20]} [{dur_str}]"
        keyboard.add(InlineKeyboardButton(button_text, callback_data=f"music_song_{song.get('id')}"))
    
    bot.edit_message_text(f"🎵 <b>Search Results for</b>: {query}\n\nSelect a song to download (FREE):",
                          chat_id=message.chat.id, message_id=searching_msg.message_id,
                          reply_markup=keyboard, parse_mode="HTML")
    
    log_usage(user_id, "Music Search", query)
    user_music_state[user_id] = None

@bot.callback_query_handler(func=lambda call: call.data.startswith("music_song_"))
def handle_music_song_callback(call):
    user_id = call.from_user.id
    song_id = call.data.replace("music_song_", "")
    bot.answer_callback_query(call.id, "🔄 Fetching song...")
    
    processing_msg = bot.send_message(call.message.chat.id, "⏳ Downloading high-quality audio...")
    
    try:
        song_details = get_song_details(song_id)
        if not song_details or not song_details.get("url"):
            bot.edit_message_text("❌ Failed to get download link. Please try again.",
                                  chat_id=call.message.chat.id, message_id=processing_msg.message_id)
            return
        
        download_url = song_details["url"]
        title = song_details["title"]
        artist = song_details["artist"] or "Unknown Artist"
        duration = song_details["duration"]
        duration_formatted = song_details.get("duration_formatted", format_duration(duration))
        album = song_details.get("album", "Single")
        year = song_details.get("year", "N/A")
        
        audio_resp = requests.get(download_url, timeout=45)
        if audio_resp.status_code != 200:
            bot.edit_message_text("❌ Download failed. Server error.",
                                  chat_id=call.message.chat.id, message_id=processing_msg.message_id)
            return
        
        import hashlib
        temp_filename = f"temp_{song_id}_{hashlib.md5(title.encode()).hexdigest()[:8]}.mp3"
        with open(temp_filename, 'wb') as f:
            f.write(audio_resp.content)
        
        caption = f"""🎵 {title} 🎵

━━━━━━━━━━━━━━━━
✨ TRACK DETAILS ✨
━━━━━━━━━━━━━━━━

🎤 Artist: {artist}
⏱️ Duration: {duration_formatted}
💿 Album: {album}
📅 Year: {year}
📊 Quality: 320kbps MP3

━━━━━━━━━━━━━━━━
👨‍💻 Developer: @viedietextraa
🎧 Keep vibing!"""
        
        with open(temp_filename, 'rb') as audio:
            bot.send_audio(call.message.chat.id, audio, title=title[:60], performer=artist[:60], duration=duration, caption=caption)
        
        try:
            os.remove(temp_filename)
            bot.delete_message(call.message.chat.id, processing_msg.message_id)
        except:
            pass
        
        log_usage(user_id, "Music Download", f"{title} - {artist}")
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🎵 New Search", callback_data="music_new_search"))
        bot.send_message(call.message.chat.id, "✅ Song sent! Want more? Tap below 👇", reply_markup=markup)
        
    except Exception as e:
        logger.error(f"Music download error: {e}")
        bot.edit_message_text(f"❌ Error: {str(e)[:200]}", chat_id=call.message.chat.id, message_id=processing_msg.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "music_new_search")
def music_new_search_callback(call):
    user_id = call.from_user.id
    user_music_state[user_id] = "waiting_for_search"
    bot.answer_callback_query(call.id, "🔍 Ready to search!")
    bot.send_message(call.message.chat.id, "🎵 Enter song or artist name:")

# ---------- Admin Commands ----------
@bot.message_handler(commands=['addcoins'])
def add_coins_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⛔ Admin only!")
        return
    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "❌ Usage: /addcoins @username amount")
            return
        identifier = parts[1].lstrip('@')
        amount = int(parts[2])
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        if identifier.isdigit():
            c.execute('SELECT user_id, username, balance FROM users WHERE user_id = ?', (int(identifier),))
        else:
            c.execute('SELECT user_id, username, balance FROM users WHERE username = ?', (identifier,))
        row = c.fetchone()
        conn.close()
        if not row:
            bot.reply_to(message, f"❌ User not found: {identifier}")
            return
        uid, uname, bal = row
        update_user_balance(uid, amount)
        new_bal = bal + amount
        bot.reply_to(message, f"✅ Added {amount} coins to @{uname} (ID: {uid})\n💰 New balance: {new_bal}")
        try:
            bot.send_message(uid, f"🎁 Admin added <b>+{amount}</b> coins to your account!\n💰 New balance: {new_bal}", parse_mode="HTML")
        except:
            pass
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['removecoins'])
def remove_coins_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⛔ Admin only!")
        return
    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "❌ Usage: /removecoins @username amount")
            return
        identifier = parts[1].lstrip('@')
        amount = int(parts[2])
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        if identifier.isdigit():
            c.execute('SELECT user_id, username, balance FROM users WHERE user_id = ?', (int(identifier),))
        else:
            c.execute('SELECT user_id, username, balance FROM users WHERE username = ?', (identifier,))
        row = c.fetchone()
        conn.close()
        if not row:
            bot.reply_to(message, f"❌ User not found: {identifier}")
            return
        uid, uname, bal = row
        if bal - amount < 0:
            bot.reply_to(message, f"❌ User has only {bal} coins. Cannot remove {amount}.")
            return
        update_user_balance(uid, -amount)
        new_bal = bal - amount
        bot.reply_to(message, f"✅ Removed {amount} coins from @{uname} (ID: {uid})\n💰 New balance: {new_bal}")
        try:
            bot.send_message(uid, f"💸 Admin removed <b>-{amount}</b> coins from your account.\n💰 New balance: {new_bal}", parse_mode="HTML")
        except:
            pass
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['broadcast'])
def broadcast_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⛔ Admin only!")
        return
    msg = message.text.replace('/broadcast', '', 1).strip()
    if not msg:
        bot.reply_to(message, "❌ Please provide a message to broadcast.")
        return
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT user_id FROM users')
    users = c.fetchall()
    conn.close()
    if not users:
        bot.reply_to(message, "❌ No users to broadcast.")
        return
    sent = 0
    for (uid,) in users:
        try:
            bot.send_message(uid, f"📢 <b>Broadcast</b>\n\n{msg}", parse_mode="HTML")
            sent += 1
            time.sleep(0.1)
        except:
            pass
    bot.reply_to(message, f"✅ Broadcast sent to {sent}/{len(users)} users.")

@bot.message_handler(commands=['setcost'])
def setcost_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⛔ Admin only!")
        return
    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "❌ Usage: /setcost module amount")
            return
        module = parts[1].lower()
        amount = int(parts[2])
        if module not in DEFAULT_COSTS:
            bot.reply_to(message, f"❌ Invalid module. Available: {', '.join(DEFAULT_COSTS.keys())}")
            return
        set_config(f"{module}_cost", str(amount))
        bot.reply_to(message, f"✅ Cost for {module} set to {amount} credits.")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['giveallcoins'])
def give_all_coins_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⛔ Admin only!")
        return
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Usage: /giveallcoins <amount>")
            return
        amount = int(parts[1])
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('SELECT user_id FROM users')
        users = c.fetchall()
        conn.close()
        if not users:
            bot.reply_to(message, "❌ No users found.")
            return
        for (uid,) in users:
            update_user_balance(uid, amount)
        bot.reply_to(message, f"✅ Added {amount} coins to all {len(users)} users.")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['checkref'])
def check_referrals_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⛔ Admin only!")
        return
    try:
        check_and_award_referrals()
        bot.reply_to(message, "✅ Referral check executed successfully.")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# ==================== Back to menu ====================
@bot.callback_query_handler(func=lambda call: call.data == "back_menu")
def back_to_menu(call):
    user = call.from_user
    user_id = user.id
    balance = get_user_balance(user_id)
    is_admin = (user_id == ADMIN_ID)
    text = main_menu_text(user_id, user.first_name, balance, "ACTIVE")
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, text, reply_markup=main_menu_keyboard(is_admin), parse_mode="HTML")
    bot.answer_callback_query(call.id)

# ==================== /cancel ====================
@bot.message_handler(commands=['cancel'])
def cancel_cmd(message):
    user_id = message.from_user.id
    
    # Check Yoga OTP session
    if user_yoga_state.get(user_id) == "waiting_otp":
        data = user_yoga_otp_data.get(user_id, {})
        cost = data.get("cost", get_module_cost("yoga"))
        update_user_balance(user_id, cost)  # REFUND
        user_yoga_state[user_id] = None
        user_yoga_otp_data.pop(user_id, None)
        bot.reply_to(message, "🔄 Yoga OTP cancelled. Credits refunded.")
        return
    
    if user_yoga_state.get(user_id) == "waiting_phone":
        cost = get_module_cost("yoga")
        update_user_balance(user_id, cost)  # REFUND
        user_yoga_state[user_id] = None
        bot.reply_to(message, "🔄 Yoga referral cancelled. Credits refunded.")
        return
    
    # Check Shopsy OTP session
    if user_shopsy_state.get(user_id) == "waiting_otp":
        data = user_shopsy_otp_data.get(user_id, {})
        cost = data.get("cost", get_module_cost("shopsy"))
        update_user_balance(user_id, cost)  # REFUND
        user_shopsy_state[user_id] = None
        user_shopsy_otp_data.pop(user_id, None)
        bot.reply_to(message, "🔄 Shopsy OTP cancelled. Credits refunded.")
        return
    
    if user_shopsy_state.get(user_id) == "waiting_phone":
        cost = get_module_cost("shopsy")
        update_user_balance(user_id, cost)  # REFUND
        user_shopsy_state[user_id] = None
        bot.reply_to(message, "🔄 Shopsy mining cancelled. Credits refunded.")
        return
    
    if user_music_state.get(user_id):
        user_music_state[user_id] = None
        bot.reply_to(message, "❌ Music search cancelled.")
    elif user_firebase_state.get(user_id):
        user_firebase_state[user_id] = False
        bot.reply_to(message, "❌ Firebase upload cancelled.")
    elif user_igviewer_state.get(user_id):
        user_igviewer_state[user_id] = None
        igviewer_data.pop(user_id, None)
        bot.reply_to(message, "❌ Instagram Viewer cancelled.")
    else:
        bot.reply_to(message, "No active operation to cancel.")

# ==================== Fallback ====================
@bot.message_handler(func=lambda m: True)
def fallback(message):
    bot.reply_to(message, "❓ Unknown command. Use /start to see the menu.")

# ==================== SCHEDULED TASKS ====================
def run_scheduled_tasks():
    while True:
        try:
            check_and_award_referrals()
            time.sleep(3600)
        except Exception as e:
            logger.error(f"Scheduled task error: {e}")
            time.sleep(60)

# ==================== MAIN ====================
if __name__ == "__main__":
    init_db()
    task_thread = threading.Thread(target=run_scheduled_tasks, daemon=True)
    task_thread.start()
    logger.info("🤖 Bot started – All features fixed!")
    logger.info("💰 Credit refund on failure enabled")
    logger.info("🧘 Yoga: Accepts both link and direct code")
    logger.info("🔄 Abort buttons added for OTP sessions")
    
    try:
        bot.remove_webhook()
        time.sleep(1)
    except:
        pass
    
    while True:
        try:
            bot.polling(non_stop=False, interval=1, timeout=30)
        except Exception as e:
            logger.error(f"Polling error: {e}")
            time.sleep(5)
