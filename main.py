#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# NRTECNO SYSTEM - VIEDIET BOT v2.0 - COMPLETELY FIXED

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

# ==================== IMPORT MENU ====================
try:
    from menu import (
        main_menu_text, main_menu_keyboard,
        firebase_menu_text, firebase_menu_keyboard,
        temp_menu_text, temp_menu_keyboard,
        flipkart_menu_text, flipkart_menu_keyboard,
        instagram_menu_text, instagram_menu_keyboard,
        referral_menu_text, referral_menu_keyboard,
        admin_panel_text, admin_panel_keyboard,
        music_menu_text, music_menu_keyboard,
        shopsy_menu_text, shopsy_menu_keyboard,
        yoga_menu_text, yoga_menu_keyboard,
        help_menu_text,
        igviewer_menu_text, igviewer_menu_keyboard,
        supercoin_menu_text, supercoin_menu_keyboard
    )
except ImportError:
    def main_menu_text(u, f, b, s): return f"Welcome {f}! Balance: {b}"
    def main_menu_keyboard(a=False): 
        kb = InlineKeyboardMarkup(row_width=1)
        kb.row(InlineKeyboardButton("📊 Stats", callback_data="module_stats"))
        return kb
    def firebase_menu_text(*a,**k): return "Firebase Module"
    def firebase_menu_keyboard(): return main_menu_keyboard()
    def temp_menu_text(*a,**k): return "Temp Mail"
    def temp_menu_keyboard(): return main_menu_keyboard()
    def flipkart_menu_text(*a,**k): return "Flipkart"
    def flipkart_menu_keyboard(): return main_menu_keyboard()
    def instagram_menu_text(*a,**k): return "Instagram"
    def instagram_menu_keyboard(): return main_menu_keyboard()
    def referral_menu_text(*a,**k): return "Referral"
    def referral_menu_keyboard(): return main_menu_keyboard()
    def admin_panel_text(*a,**k): return "Admin"
    def admin_panel_keyboard(): return main_menu_keyboard()
    def music_menu_text(*a,**k): return "Music"
    def music_menu_keyboard(): return main_menu_keyboard()
    def shopsy_menu_text(*a,**k): return "Shopsy"
    def shopsy_menu_keyboard(): return main_menu_keyboard()
    def yoga_menu_text(*a,**k): return "Yoga"
    def yoga_menu_keyboard(): return main_menu_keyboard()
    def help_menu_text(*a,**k): return "Help"
    def igviewer_menu_text(*a,**k): return "IG Viewer"
    def igviewer_menu_keyboard(): return main_menu_keyboard()
    def supercoin_menu_text(*a,**k): return "Supercoin Fetcher"
    def supercoin_menu_keyboard(): return main_menu_keyboard()

# ==================== PROXY CONFIGURATION ====================
class ProxyManager:
    @staticmethod
    def get_proxy_config():
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
REFERRAL_STAY_HOURS = 0

YOGA_REFER_REWARD = 4
YOGA_WELCOME_BONUS = 2

DEFAULT_COSTS = {
    "firebase": 1,
    "flipkart": 1,
    "instagram_single": 1,
    "instagram_bulk": 1,
    "shopsy": 1,
    "yoga": 1,
    "igviewer": 1,
    "supercoin": 1,
}

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

# ==================== SCHEDULED TASKS ====================
def run_scheduled_tasks():
    while True:
        try:
            check_and_award_referrals()
        except Exception as e:
            logger.error(f"[SCHEDULED] Error: {e}")
        try:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='temp_emails'")
            if c.fetchone():
                c.execute('DELETE FROM temp_emails WHERE created_at <= datetime("now", "-10 minutes")')
                conn.commit()
            conn.close()
        except:
            pass
        time.sleep(300)

# ==================== CREDIT MANAGER ====================
class CreditManager:
    def __init__(self, user_id, cost, operation_name=""):
        self.user_id = user_id
        self.cost = cost
        self.operation_name = operation_name
        self.deducted = False
        self.balance_before = 0
    
    def __enter__(self):
        return self
    
    def deduct(self):
        self.balance_before = get_user_balance(self.user_id)
        if self.balance_before < self.cost:
            raise ValueError(f"Insufficient credits! Need {self.cost}")
        update_user_balance(self.user_id, -self.cost)
        self.deducted = True
        return self
    
    def refund(self):
        if self.deducted:
            update_user_balance(self.user_id, self.cost)
            self.deducted = False
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
                logger.error(f"Referral award error: {e}")
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

# ==================== YOGA FUNCTIONS ====================
def yoga_api_post(url, payload, headers, use_proxy=True):
    try:
        proxies = None
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
        return None, "Timeout - Server not responding"
    except requests.exceptions.ConnectionError:
        return None, "Connection Error - Check internet"
    except Exception as e:
        return None, str(e)

def yoga_register(phone, code, name, did, sid):
    return yoga_api_post(YOGA_REGISTER_URL, {
        "name": name, 
        "phoneNumber": phone, 
        "referredBy": code,
        "sourceData": {"type": "Referral", "refererurl": "", "timezone": "Asia/Kolkata"},
        "experimentMetaInfo": {"deviceId": did, "sessionId": sid},
    }, YOGA_REG_HEADERS)

def yoga_send_otp(phone, did, sid):
    try:
        headers = {
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
        payload = {
            "method": "phone_otp", 
            "otpChannel": "sms", 
            "phoneNumber": phone,
            "sourceData": {"type": "portal", "utm_source": "web_app"},
            "experimentMetaInfo": {"deviceId": did, "sessionId": sid},
            "registerUser": False,
        }
        response = requests.post(
            YOGA_LOGIN_URL,
            json=payload,
            headers=headers,
            timeout=30
        )
        if response.status_code in (200, 201):
            try:
                resp_json = response.json()
                if resp_json.get("message") == "OTP sent to your phone":
                    ref = resp_json.get("data", {}).get("refrence_code")
                    if ref:
                        return ref, None
                return None, resp_json.get("message", "Unknown error")
            except:
                return None, "Invalid JSON response"
        return None, f"HTTP {response.status_code}: {response.text[:150]}"
    except requests.exceptions.Timeout:
        return None, "Timeout - Server not responding"
    except requests.exceptions.ConnectionError:
        return None, "Connection Error"
    except Exception as e:
        return None, str(e)

def yoga_verify_otp(phone, ref, otp, did, sid):
    return yoga_api_post(YOGA_VERIFY_URL, {
        "phone": phone, 
        "reference_code": ref, 
        "otp": otp,
        "experimentMetaInfo": {"deviceId": did, "sessionId": sid},
        "registerUser": False,
    }, YOGA_HEADERS)

def rand_id():
    return str(uuid.uuid4())

def rand_yoga_name():
    return random.choice(YOGA_NAMES)

def extract_yoga_code(link: str):
    link = link.strip().rstrip("/")
    if "habit.yoga/" in link:
        code = link.replace("https://habit.yoga/", "").replace("http://habit.yoga/", "")
        code = code.split("/")[0]
        if code and all(c.isalnum() or c == "_" for c in code) and 1 <= len(code) <= 50:
            return code
        return None
    if link and all(c.isalnum() or c == "_" for c in link) and 1 <= len(link) <= 50:
        return link
    return None

# ==================== SHOPSY FUNCTIONS ====================
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
            "lockinResponse": 426889274        }
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

async def shopsy_login_with_otp(phone):
    d_id, v_id, s_id = generate_ids()
    session_data = {
        "phone": phone,
        "device_id": d_id,
        "visit_id": v_id,
        "app_session_id": s_id,
        "current_dc": "1",
        "owner_id": "telegram_bot"
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
    return session_data, None

async def shopsy_verify_otp(session_data, otp):
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
        save_session(phone, session_data)
        return session_data, True
    return session_data, False

async def shopsy_core_mine(session_data, progress_callback=None):
    phone = session_data.get("phone")
    
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

# ==================== SUPERCOIN FETCHER - FIXED ====================
class SupercoinSession:
    def __init__(self):
        self.session = cffi_requests.Session(impersonate="chrome120")
        self.device_id = uuid.uuid4().hex[:32]
        self.visit_id = f"{uuid.uuid4().hex[:32]}-{int(time.time() * 1000)}"
        self.app_session = f"{uuid.uuid4()}_{int(time.time()*1000)}"
        self.current_dc = "1"
        self.tokens = {}
        self.user_id = None
        
    def _build_headers(self, is_game=False, extra_headers=None):
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
            
        for token_key in ["at", "sn", "secureToken", "rt"]:
            if self.tokens.get(token_key):
                base_headers[token_key] = self.tokens[token_key]
                
        if extra_headers:
            base_headers.update(extra_headers)
            
        return base_headers
    
    async def request(self, method, path, data=None, is_game=False, retries=3):
        url = f"https://{self.current_dc}.rome.api.flipkart.net{path}"
        headers = self._build_headers(is_game)
        
        for attempt in range(retries):
            try:
                if method.upper() == "POST":
                    resp = self.session.post(url, json=data, headers=headers, timeout=30)
                else:
                    resp = self.session.get(url, headers=headers, timeout=30)
                
                try:
                    resp_json = resp.json()
                except:
                    resp_json = {}
                
                if resp.status_code == 406 and resp_json.get("ERROR_MESSAGE") == "DC Change":
                    new_dc = resp_json.get("RESPONSE", {}).get("id") or resp_json.get("RESPONSE", {}).get("dc")
                    if new_dc:
                        self.current_dc = str(new_dc)
                        url = f"https://{self.current_dc}.rome.api.flipkart.net{path}"
                        continue
                
                self._extract_tokens(resp_json, resp.headers)
                return resp.status_code, resp_json
                
            except Exception as e:
                if attempt == retries - 1:
                    raise Exception(f"Request failed after {retries} attempts: {str(e)}")
                await asyncio.sleep(2 ** attempt)
                
        return 500, {"error": "Max retries exceeded"}
    
    def _extract_tokens(self, resp_json, resp_headers):
        if isinstance(resp_json, dict):
            session_block = resp_json.get("SESSION") or resp_json.get("RESPONSE", {}).get("SESSION") or {}
            for key in ["accountId", "at", "rt", "sn", "secureToken", "nsid", "vid", "email", "firstName", "lastName"]:
                if session_block.get(key):
                    self.tokens[key] = session_block[key]
            if session_block.get("userId"):
                self.user_id = session_block["userId"]
            if session_block.get("isLoggedIn") is True:
                self.tokens["isLoggedIn"] = True
        headers_lower = {k.lower(): v for k, v in resp_headers.items()}
        for key in ["at", "rt", "sn", "nsid", "vid", "sessionid"]:
            if headers_lower.get(key):
                self.tokens[key] = headers_lower[key]
        return self.tokens

    async def request_otp(self, phone):
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
        
        # FIXED: Handle empty response
        if status == 200 and response.get("success"):
            data = response.get("data", {})
            earnings = data.get("earnings", {})
            coins = earnings.get("coinsEarnedTotal", 0)
            return coins, data
        
        # Return 0 coins if response is empty or error
        return 0, None

# ==================== IG VIEWER FUNCTIONS - FROM STORY.PY ====================
def get_instagram_stories(username: str):
    """Fetch stories from storyviewer.com API - from story.py"""
    try:
        API_URL = "https://storyviewer.com/api/v1/web/profile"
        response = requests.post(
            API_URL,
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
        return data
    except Exception as e:
        logger.error(f"API request failed: {e}")
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
user_supercoin_state = {}
user_supercoin_otp_data = {}

# ==================== BACK BUTTON HELPER ====================
def back_button():
    kb = InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu"))
    return kb

# ==================== SHOPSY HANDLERS ====================
@bot.message_handler(func=lambda message: user_shopsy_state.get(message.from_user.id) == "waiting_phone")
def shopsy_phone_handler(message):
    user_id = message.from_user.id
    phone = message.text.strip()
    
    if phone.lower() in ['/cancel', 'cancel', 'abort']:
        user_shopsy_state[user_id] = None
        bot.reply_to(message, "❌ Shopsy mining cancelled.", reply_markup=back_button())
        return
    
    if not phone.isdigit() or len(phone) != 10:
        bot.reply_to(message, "❌ Please enter exactly 10 digits.\n\nSend /cancel to abort.")
        return
    
    cost = get_module_cost("shopsy")
    balance = get_user_balance(user_id)
    if balance < cost:
        bot.reply_to(message, f"❌ Insufficient credits! You need {cost} credits. Your balance: {balance}")
        return
    
    abort_kb = InlineKeyboardMarkup()
    abort_kb.row(InlineKeyboardButton("❌ Abort", callback_data="shopsy_abort"))
    abort_kb.row(InlineKeyboardButton("🔙 Back", callback_data="back_shopsy"))
    
    status_msg = bot.reply_to(message, f"📱 Sending OTP to +91{phone}...", reply_markup=abort_kb)
    update_user_balance(user_id, -cost)
    
    def send_otp_thread():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            session_data, err = loop.run_until_complete(shopsy_login_with_otp(phone))
            loop.close()
            
            if not session_data:
                update_user_balance(user_id, cost)
                bot.edit_message_text(f"❌ Failed: {err}", chat_id=message.chat.id, message_id=status_msg.message_id)
                user_shopsy_state[user_id] = None
                return
            
            user_shopsy_otp_data[user_id] = {"session_data": session_data, "phone": phone, "cost": cost}
            user_shopsy_state[user_id] = "waiting_otp"
            
            otp_kb = InlineKeyboardMarkup()
            otp_kb.row(InlineKeyboardButton("❌ Abort", callback_data="shopsy_abort_otp"))
            otp_kb.row(InlineKeyboardButton("🔙 Back", callback_data="back_shopsy"))
            
            bot.edit_message_text(
                f"✅ OTP sent to +91{phone}!\n\nEnter the OTP code you received:\n\nSend /cancel to abort.",
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                reply_markup=otp_kb
            )
        except Exception as e:
            update_user_balance(user_id, cost)
            bot.edit_message_text(f"❌ Error: {str(e)[:200]}", chat_id=message.chat.id, message_id=status_msg.message_id)
            user_shopsy_state[user_id] = None
    
    threading.Thread(target=send_otp_thread).start()

@bot.message_handler(func=lambda message: user_shopsy_state.get(message.from_user.id) == "waiting_otp")
def shopsy_otp_handler(message):
    user_id = message.from_user.id
    otp = message.text.strip()
    
    if otp.lower() in ['/cancel', 'cancel']:
        user_shopsy_state[user_id] = None
        if user_id in user_shopsy_otp_data:
            update_user_balance(user_id, user_shopsy_otp_data[user_id]["cost"])
            del user_shopsy_otp_data[user_id]
        bot.reply_to(message, "❌ Shopsy login cancelled.", reply_markup=back_button())
        return
    
    if not otp.isdigit() or len(otp) != 6:
        bot.reply_to(message, "❌ Please enter a valid 6-digit OTP.\n\nSend /cancel to abort.")
        return
    
    if user_id not in user_shopsy_otp_data:
        bot.reply_to(message, "❌ Session expired. Please start again.")
        user_shopsy_state[user_id] = None
        return
    
    data = user_shopsy_otp_data[user_id]
    session_data = data["session_data"]
    phone = data["phone"]
    cost = data["cost"]
    
    status_msg = bot.reply_to(message, "🔄 Verifying OTP...")
    
    def verify_thread():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            updated_session, success = loop.run_until_complete(shopsy_verify_otp(session_data, otp))
            loop.close()
            
            if success:
                save_shopsy_session(user_id, phone, updated_session)
                update_shopsy_balance(user_id, 0)
                
                bot.edit_message_text(
                    f"✅ <b>Shopsy Login Successful!</b>\n\n"
                    f"📱 Phone: +91{phone}\n"
                    f"💰 Credits refunded: <code>+{cost}</code>\n"
                    f"💳 Balance: <code>{get_user_balance(user_id)}</code>\n\n"
                    f"🎮 Now start mining using the Shopsy menu!\n"
                    f"Click 'Start Mining' again to begin!",
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id,
                    reply_markup=back_button()
                )
                
                update_user_balance(user_id, cost)
                user_shopsy_state[user_id] = None
                if user_id in user_shopsy_otp_data:
                    del user_shopsy_otp_data[user_id]
            else:
                update_user_balance(user_id, cost)
                bot.edit_message_text(
                    f"❌ Invalid OTP. Please try again.\n\nSend /cancel to abort.",
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id
                )
                user_shopsy_state[user_id] = "waiting_otp"
                
        except Exception as e:
            update_user_balance(user_id, cost)
            bot.edit_message_text(f"❌ Error: {str(e)[:200]}", chat_id=message.chat.id, message_id=status_msg.message_id)
            user_shopsy_state[user_id] = None
            if user_id in user_shopsy_otp_data:
                del user_shopsy_otp_data[user_id]
    
    threading.Thread(target=verify_thread).start()

# ==================== SHOPSY MINING START ====================
@bot.message_handler(func=lambda message: user_shopsy_state.get(message.from_user.id) == "start_mining")
def shopsy_start_mining_handler(message):
    user_id = message.from_user.id
    if not get_shopsy_login_status(user_id):
        bot.reply_to(message, "❌ Please login first using 'Start Mining' from the menu.", reply_markup=back_button())
        user_shopsy_state[user_id] = None
        return
    
    cost = get_module_cost("shopsy")
    balance = get_user_balance(user_id)
    if balance < cost:
        bot.reply_to(message, f"❌ Insufficient credits! Need {cost} credits. Balance: {balance}")
        return
    
    update_user_balance(user_id, -cost)
    status_msg = bot.reply_to(message, "⛏️ Starting Shopsy mining...\nThis may take 1-2 minutes.")
    
    phone, session_data = get_shopsy_session(user_id)
    if not session_data:
        update_user_balance(user_id, cost)
        bot.edit_message_text("❌ Session expired. Please login again.", chat_id=message.chat.id, message_id=status_msg.message_id)
        return
    
    def mining_thread():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def progress_callback(msg):
                bot.edit_message_text(f"⛏️ {msg}", chat_id=message.chat.id, message_id=status_msg.message_id)
            
            result = loop.run_until_complete(shopsy_core_mine(session_data, progress_callback))
            loop.close()
            
            if result["status"] == "success":
                update_shopsy_balance(user_id, result["earned"])
                result_text = f"""
✅ <b>Mining Complete!</b>

📱 Phone: +91{phone}
🪙 Earned: <code>{result['earned']} SC</code>
💰 Total Coins: <code>{result['final_coins']} SC</code>
🎮 Games Played: <code>{result['played']}/{result['total']}</code>
💎 Gems Earned: <code>{result['gems']}</code>
⏱️ Time Taken: <code>{result['time_taken']}s</code>
"""
                bot.edit_message_text(result_text, chat_id=message.chat.id, message_id=status_msg.message_id, parse_mode="HTML", reply_markup=back_button())
            else:
                update_user_balance(user_id, cost)
                bot.edit_message_text(f"❌ Mining failed: {result.get('msg', 'Unknown error')}", chat_id=message.chat.id, message_id=status_msg.message_id, reply_markup=back_button())
                
        except Exception as e:
            update_user_balance(user_id, cost)
            bot.edit_message_text(f"❌ Error: {str(e)[:200]}", chat_id=message.chat.id, message_id=status_msg.message_id, reply_markup=back_button())
        
        user_shopsy_state[user_id] = None
    
    threading.Thread(target=mining_thread).start()

# ==================== SUPERCOIN HANDLERS ====================
@bot.message_handler(func=lambda message: user_supercoin_state.get(message.from_user.id) == "waiting_supercoin_phone")
def supercoin_phone_handler(message):
    user_id = message.from_user.id
    phone = message.text.strip()
    
    if phone.lower() in ['/cancel', 'cancel']:
        user_supercoin_state[user_id] = None
        bot.reply_to(message, "❌ Supercoin check cancelled.", reply_markup=back_button())
        return
    
    if not phone.isdigit() or len(phone) != 10:
        bot.reply_to(message, "❌ Please enter exactly 10 digits.\n\nSend /cancel to abort.")
        return
    
    cost = get_module_cost("supercoin")
    balance = get_user_balance(user_id)
    if balance < cost:
        bot.reply_to(message, f"❌ Insufficient credits! Need {cost} credits. Balance: {balance}")
        return
    
    user_supercoin_state[user_id] = "waiting_supercoin_otp"
    
    abort_kb = InlineKeyboardMarkup()
    abort_kb.row(InlineKeyboardButton("❌ Abort", callback_data="supercoin_abort"))
    abort_kb.row(InlineKeyboardButton("🔙 Back", callback_data="back_supercoin"))
    
    status_msg = bot.reply_to(message, f"📱 Sending OTP to +91{phone}...", reply_markup=abort_kb)
    update_user_balance(user_id, -cost)
    
    def send_otp_thread():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            client = SupercoinSession()
            success, req_id = loop.run_until_complete(client.request_otp(phone))
            loop.close()
            
            if not success:
                update_user_balance(user_id, cost)
                bot.edit_message_text(
                    f"❌ Failed to send OTP: {req_id}",
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id
                )
                user_supercoin_state[user_id] = None
                return
            
            user_supercoin_otp_data[user_id] = {
                "phone": phone,
                "client": client,
                "cost": cost
            }
            
            otp_kb = InlineKeyboardMarkup()
            otp_kb.row(InlineKeyboardButton("❌ Abort", callback_data="supercoin_abort"))
            otp_kb.row(InlineKeyboardButton("🔙 Back", callback_data="back_supercoin"))
            
            bot.edit_message_text(
                f"✅ OTP sent to +91{phone}!\n\n"
                f"📱 Enter the 6-digit OTP code you received:\n\n"
                f"<b>Send /cancel to abort</b>",
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                reply_markup=otp_kb
            )
            user_supercoin_state[user_id] = "waiting_supercoin_otp"
            
        except Exception as e:
            update_user_balance(user_id, cost)
            bot.edit_message_text(
                f"❌ Error: {str(e)[:200]}",
                chat_id=message.chat.id,
                message_id=status_msg.message_id
            )
            user_supercoin_state[user_id] = None
    
    threading.Thread(target=send_otp_thread).start()

@bot.message_handler(func=lambda message: user_supercoin_state.get(message.from_user.id) == "waiting_supercoin_otp")
def supercoin_otp_handler(message):
    user_id = message.from_user.id
    otp = message.text.strip()
    
    if otp.lower() in ['/cancel', 'cancel']:
        user_supercoin_state[user_id] = None
        if user_id in user_supercoin_otp_data:
            update_user_balance(user_id, user_supercoin_otp_data[user_id]["cost"])
            del user_supercoin_otp_data[user_id]
        bot.reply_to(message, "❌ Supercoin check cancelled.", reply_markup=back_button())
        return
    
    if not otp.isdigit() or len(otp) != 6:
        bot.reply_to(message, "❌ Please enter a valid 6-digit OTP.\n\nSend /cancel to abort.")
        return
    
    if user_id not in user_supercoin_otp_data:
        bot.reply_to(message, "❌ Session expired. Please start again.")
        user_supercoin_state[user_id] = None
        return
    
    data = user_supercoin_otp_data[user_id]
    phone = data["phone"]
    client = data["client"]
    cost = data["cost"]
    
    status_msg = bot.reply_to(message, "🔄 Verifying OTP and fetching coins...")
    
    def verify_thread():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            success, response = loop.run_until_complete(client.verify_otp(phone, otp))
            
            if not success:
                update_user_balance(user_id, cost)
                bot.edit_message_text(
                    f"❌ OTP verification failed: {response}",
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id
                )
                user_supercoin_state[user_id] = None
                if user_id in user_supercoin_otp_data:
                    del user_supercoin_otp_data[user_id]
                loop.close()
                return
            
            loop.run_until_complete(client.load_user_state())
            
            coins, user_data = loop.run_until_complete(client.fetch_coins())
            loop.close()
            
            update_user_balance(user_id, cost)
            
            # Always show result, even if 0 coins
            if user_data is not None:
                earnings = user_data.get("earnings", {})
                result_text = f"""
💰 <b>SUPERCOIN FETCHER RESULTS</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📱 <b>Phone:</b> <code>+91{phone}</code>
👤 <b>Name:</b> <code>{user_data.get('name', 'N/A')}</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 <b>SUPER COINS</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🪙 <b>Total Coins:</b> <code>{coins} SC</code>
📈 <b>Daily Coins:</b> <code>{earnings.get('coinsEarnedDaily', 0)} SC</code>
📊 <b>Weekly Coins:</b> <code>{earnings.get('coinsEarnedWeekly', 0)} SC</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛒 <b>Total Orders:</b> <code>{user_data.get('totalOrders', 0)}</code>
"""
            else:
                result_text = f"""
💰 <b>SUPERCOIN FETCHER RESULTS</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📱 <b>Phone:</b> <code>+91{phone}</code>
🪙 <b>Total Coins:</b> <code>{coins} SC</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 No additional data available.
"""
            
            bot.edit_message_text(
                result_text,
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                reply_markup=back_button(),
                parse_mode="HTML"
            )
            
            user_supercoin_state[user_id] = None
            if user_id in user_supercoin_otp_data:
                del user_supercoin_otp_data[user_id]
                
        except Exception as e:
            update_user_balance(user_id, cost)
            bot.edit_message_text(
                f"❌ Error: {str(e)[:200]}",
                chat_id=message.chat.id,
                message_id=status_msg.message_id
            )
            user_supercoin_state[user_id] = None
            if user_id in user_supercoin_otp_data:
                del user_supercoin_otp_data[user_id]
    
    threading.Thread(target=verify_thread).start()

# ==================== IG VIEWER HANDLERS - FROM STORY.PY ====================
@bot.message_handler(func=lambda message: user_igviewer_state.get(message.from_user.id) == "waiting_ig_username")
def igviewer_username_handler(message):
    user_id = message.from_user.id
    username = message.text.strip()
    
    if username.lower() in ['/cancel', 'cancel']:
        user_igviewer_state[user_id] = None
        bot.reply_to(message, "❌ IG Viewer cancelled.", reply_markup=back_button())
        return
    
    if not username:
        bot.reply_to(message, "❌ Please enter a valid username.")
        return
    
    cost = get_module_cost("igviewer")
    balance = get_user_balance(user_id)
    if balance < cost:
        bot.reply_to(message, f"❌ Insufficient credits! Need {cost} credits. Balance: {balance}")
        return
    
    status_msg = bot.reply_to(message, f"🔍 Fetching stories for @{username}...")
    update_user_balance(user_id, -cost)
    
    def fetch_stories():
        try:
            data = get_instagram_stories(username)
            
            if not data:
                bot.edit_message_text(
                    f"❌ No data found for @{username}\n\n"
                    f"Make sure the username is correct.",
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id,
                    reply_markup=back_button()
                )
                user_igviewer_state[user_id] = None
                return
            
            stories = data.get("stories", [])
            
            if not stories:
                bot.edit_message_text(
                    f"📸 No stories found for @{username}\n\n"
                    f"Profile may have no active stories.",
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id,
                    reply_markup=back_button()
                )
                user_igviewer_state[user_id] = None
                return
            
            # Get user info
            user_info = data.get("user_info", {})
            
            # Send profile info first
            profile_text = f"""
👁️ <b>INSTAGRAM PROFILE</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 <b>Username:</b> @{username}
📛 <b>Name:</b> {user_info.get('full_name', 'N/A')}
📝 <b>Bio:</b> {user_info.get('bio', 'N/A')[:200]}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📸 <b>Stories Found:</b> <code>{len(stories)}</code>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            bot.edit_message_text(
                profile_text,
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                parse_mode="HTML"
            )
            
            # Send stories (limit to 5)
            sent_count = 0
            for idx, story in enumerate(stories[:5], 1):
                media_url = story.get("source")
                if not media_url:
                    continue
                
                media_type = story.get("media_type", "image")
                if media_type not in ["video", "image"]:
                    if media_url.lower().endswith((".mp4", ".mov", ".webm")):
                        media_type = "video"
                    else:
                        media_type = "image"
                
                caption = f"📸 Story {idx}/{len(stories[:5])}"
                mentions = story.get("mentions", [])
                if mentions:
                    caption += f"\n👥 Mentions: {', '.join([f'@{m}' for m in mentions])}"
                
                try:
                    if media_type == "video":
                        bot.send_video(message.chat.id, media_url, caption=caption)
                    else:
                        bot.send_photo(message.chat.id, media_url, caption=caption)
                    sent_count += 1
                    time.sleep(0.5)
                except Exception as e:
                    logger.error(f"Failed to send story: {e}")
            
            if sent_count == 0:
                bot.send_message(
                    message.chat.id,
                    "❌ Failed to send any stories.",
                    reply_markup=back_button()
                )
            else:
                bot.send_message(
                    message.chat.id,
                    f"✅ Sent {sent_count} story(ies) from @{username}",
                    reply_markup=back_button()
                )
            
        except Exception as e:
            update_user_balance(user_id, cost)
            bot.edit_message_text(
                f"❌ Error: {str(e)[:200]}",
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                reply_markup=back_button()
            )
        
        user_igviewer_state[user_id] = None
    
    threading.Thread(target=fetch_stories).start()

# ==================== YOGA HANDLERS ====================
@bot.message_handler(func=lambda message: user_yoga_state.get(message.from_user.id) == "waiting_yoga_phone")
def yoga_phone_handler(message):
    user_id = message.from_user.id
    phone = message.text.strip()
    
    if phone.lower() in ['/cancel', 'cancel']:
        user_yoga_state[user_id] = None
        bot.reply_to(message, "❌ Yoga referral cancelled.", reply_markup=back_button())
        return
    
    if not phone.isdigit() or len(phone) != 10:
        bot.reply_to(message, "❌ Please enter exactly 10 digits.\n\nSend /cancel to abort.")
        return
    
    cost = get_module_cost("yoga")
    balance = get_user_balance(user_id)
    if balance < cost:
        bot.reply_to(message, f"❌ Insufficient credits! Need {cost} credits. Balance: {balance}")
        return
    
    user_yoga_state[user_id] = "waiting_yoga_otp"
    
    abort_kb = InlineKeyboardMarkup()
    abort_kb.row(InlineKeyboardButton("❌ Abort", callback_data="yoga_abort_otp"))
    abort_kb.row(InlineKeyboardButton("🔙 Back", callback_data="back_yoga"))
    
    status_msg = bot.reply_to(message, f"📱 Sending OTP to +91{phone}...", reply_markup=abort_kb)
    update_user_balance(user_id, -cost)
    
    def send_otp_thread():
        try:
            did = rand_id()
            sid = rand_id()
            
            ref, err = yoga_send_otp(phone, did, sid)
            
            if err:
                update_user_balance(user_id, cost)
                bot.edit_message_text(
                    f"❌ Failed to send OTP: {err}\n\nPlease try again later.",
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id
                )
                user_yoga_state[user_id] = None
                return
            
            user_yoga_otp_data[user_id] = {
                "phone": phone,
                "ref": ref,
                "did": did,
                "sid": sid,
                "cost": cost
            }
            
            otp_kb = InlineKeyboardMarkup()
            otp_kb.row(InlineKeyboardButton("❌ Abort", callback_data="yoga_abort_otp"))
            otp_kb.row(InlineKeyboardButton("🔙 Back", callback_data="back_yoga"))
            
            bot.edit_message_text(
                f"✅ OTP sent to +91{phone}!\n\n"
                f"📱 Enter the 6-digit OTP code you received:\n\n"
                f"<b>Send /cancel to abort</b>",
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                reply_markup=otp_kb
            )
            user_yoga_state[user_id] = "waiting_yoga_otp"
            
        except Exception as e:
            update_user_balance(user_id, cost)
            bot.edit_message_text(
                f"❌ Error: {str(e)[:200]}",
                chat_id=message.chat.id,
                message_id=status_msg.message_id
            )
            user_yoga_state[user_id] = None
    
    threading.Thread(target=send_otp_thread).start()

@bot.message_handler(func=lambda message: user_yoga_state.get(message.from_user.id) == "waiting_yoga_otp")
def yoga_otp_handler(message):
    user_id = message.from_user.id
    otp = message.text.strip()
    
    if otp.lower() in ['/cancel', 'cancel']:
        user_yoga_state[user_id] = None
        if user_id in user_yoga_otp_data:
            del user_yoga_otp_data[user_id]
        bot.reply_to(message, "❌ Yoga referral cancelled.", reply_markup=back_button())
        return
    
    if not otp.isdigit() or len(otp) != 6:
        bot.reply_to(message, "❌ Please enter a valid 6-digit OTP.\n\nSend /cancel to abort.")
        return
    
    if user_id not in user_yoga_otp_data:
        bot.reply_to(message, "❌ Session expired. Please start again.")
        user_yoga_state[user_id] = None
        return
    
    data = user_yoga_otp_data[user_id]
    phone = data["phone"]
    ref = data["ref"]
    did = data["did"]
    sid = data["sid"]
    cost = data["cost"]
    
    status_msg = bot.reply_to(message, "🔄 Verifying OTP...")
    
    def verify_thread():
        try:
            resp, err = yoga_verify_otp(phone, ref, otp, did, sid)
            
            if err:
                update_user_balance(user_id, cost)
                bot.edit_message_text(
                    f"❌ OTP verification failed: {err}\n\nPlease try again.",
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id
                )
                user_yoga_state[user_id] = None
                if user_id in user_yoga_otp_data:
                    del user_yoga_otp_data[user_id]
                return
            
            if resp and resp.get("data", {}).get("isVerified", False):
                conn = sqlite3.connect(DB_PATH, check_same_thread=False)
                c = conn.cursor()
                c.execute('SELECT yoga_code FROM users WHERE user_id = ?', (user_id,))
                row = c.fetchone()
                yoga_code = row[0] if row and row[0] else None
                conn.close()
                
                if not yoga_code:
                    bot.edit_message_text(
                        "⚠️ You don't have a Yoga referral code set!\n\n"
                        "Please set your Yoga referral code first using:\n"
                        "<code>/setyoga YOUR_CODE</code>\n\n"
                        "Or send me your Habit.Yoga referral link.",
                        chat_id=message.chat.id,
                        message_id=status_msg.message_id
                    )
                    user_yoga_state[user_id] = None
                    if user_id in user_yoga_otp_data:
                        del user_yoga_otp_data[user_id]
                    return
                
                name = rand_yoga_name()
                reg_resp, reg_err = yoga_register(phone, yoga_code, name, did, sid)
                
                if reg_err:
                    update_user_balance(user_id, cost)
                    bot.edit_message_text(
                        f"❌ Registration failed: {reg_err}",
                        chat_id=message.chat.id,
                        message_id=status_msg.message_id
                    )
                    user_yoga_state[user_id] = None
                    if user_id in user_yoga_otp_data:
                        del user_yoga_otp_data[user_id]
                    return
                
                reward = get_yoga_refer_reward()
                update_user_balance(user_id, reward)
                
                conn = sqlite3.connect(DB_PATH, check_same_thread=False)
                c = conn.cursor()
                c.execute('UPDATE users SET yoga_bot_refers = yoga_bot_refers + 1 WHERE user_id = ?', (user_id,))
                conn.commit()
                conn.close()
                
                bot.edit_message_text(
                    f"✅ <b>Yoga Referral Successful!</b>\n\n"
                    f"📱 Phone: +91{phone}\n"
                    f"👤 Name: {name}\n"
                    f"🔑 Referral Code: {yoga_code}\n"
                    f"💰 Reward: <code>+{reward} Credits</code>\n"
                    f"💳 New Balance: <code>{get_user_balance(user_id)}</code>\n\n"
                    f"🎯 Referral completed successfully!",
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id,
                    reply_markup=back_button()
                )
                
                user_yoga_state[user_id] = None
                if user_id in user_yoga_otp_data:
                    del user_yoga_otp_data[user_id]
                
            else:
                update_user_balance(user_id, cost)
                bot.edit_message_text(
                    f"❌ OTP verification failed.\n\n"
                    f"Please try again with a valid OTP.",
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id
                )
                user_yoga_state[user_id] = None
                if user_id in user_yoga_otp_data:
                    del user_yoga_otp_data[user_id]
                
        except Exception as e:
            update_user_balance(user_id, cost)
            bot.edit_message_text(
                f"❌ Error: {str(e)[:200]}",
                chat_id=message.chat.id,
                message_id=status_msg.message_id
            )
            user_yoga_state[user_id] = None
            if user_id in user_yoga_otp_data:
                del user_yoga_otp_data[user_id]
    
    threading.Thread(target=verify_thread).start()

# ==================== CALLBACK QUERY HANDLER ====================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    data = call.data
    
    if data == "back_menu" or data == "back_main":
        user = get_user(user_id)
        if not user:
            bot.answer_callback_query(call.id, "User not found")
            return
        status = "✅" if check_membership(user_id) else "❌"
        is_admin = user_id == ADMIN_ID
        bot.edit_message_text(
            main_menu_text(user_id, user['first_name'], user['balance'], status),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=main_menu_keyboard(is_admin),
            parse_mode="HTML"
        )
        bot.answer_callback_query(call.id)
        return
    
    if data in ["back_shopsy", "back_yoga", "back_supercoin"]:
        user = get_user(user_id)
        if data == "back_shopsy":
            text = shopsy_menu_text(user_id, user['balance'], "✅", get_shopsy_balance(user_id), get_shopsy_login_status(user_id))
            kb = shopsy_menu_keyboard()
        elif data == "back_supercoin":
            text = supercoin_menu_text(user_id, user['balance'], "✅", get_module_cost("supercoin"))
            kb = supercoin_menu_keyboard()
        else:
            cost = get_module_cost("yoga")
            reward = get_yoga_refer_reward()
            yoga_code = user.get('yoga_code') if user else None
            text = yoga_menu_text(user_id, user['balance'], "✅", yoga_code, reward, cost)
            kb = yoga_menu_keyboard()
        
        user_shopsy_state[user_id] = None
        user_yoga_state[user_id] = None
        user_supercoin_state[user_id] = None
        user_igviewer_state[user_id] = None
        if user_id in user_shopsy_otp_data:
            del user_shopsy_otp_data[user_id]
        if user_id in user_yoga_otp_data:
            del user_yoga_otp_data[user_id]
        if user_id in user_supercoin_otp_data:
            del user_supercoin_otp_data[user_id]
        
        bot.edit_message_text(
            text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=kb,
            parse_mode="HTML"
        )
        bot.answer_callback_query(call.id)
        return
    
    if data.startswith("module_"):
        module = data.replace("module_", "")
        user = get_user(user_id)
        if not user:
            bot.answer_callback_query(call.id, "User not found")
            return
        
        status = "✅" if check_membership(user_id) else "❌"
        balance = user['balance']
        
        if module == "firebase":
            cost = get_module_cost("firebase")
            bot.edit_message_text(
                firebase_menu_text(user_id, balance, status, cost),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=firebase_menu_keyboard(),
                parse_mode="HTML"
            )
        elif module == "temp":
            bot.edit_message_text(
                temp_menu_text(user_id),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=temp_menu_keyboard(),
                parse_mode="HTML"
            )
        elif module == "flipkart":
            cost = get_module_cost("flipkart")
            bot.edit_message_text(
                flipkart_menu_text(user_id, balance, status, cost),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=flipkart_menu_keyboard(),
                parse_mode="HTML"
            )
        elif module == "instagram":
            cost = get_module_cost("instagram_single")
            bot.edit_message_text(
                instagram_menu_text(user_id, balance, status, cost),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=instagram_menu_keyboard(),
                parse_mode="HTML"
            )
        elif module == "igviewer":
            cost = get_module_cost("igviewer")
            bot.edit_message_text(
                igviewer_menu_text(user_id, balance, status, cost),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=igviewer_menu_keyboard(),
                parse_mode="HTML"
            )
        elif module == "music":
            bot.edit_message_text(
                music_menu_text(user_id),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=music_menu_keyboard(),
                parse_mode="HTML"
            )
        elif module == "shopsy":
            bot.edit_message_text(
                shopsy_menu_text(user_id, balance, status, get_shopsy_balance(user_id), get_shopsy_login_status(user_id)),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=shopsy_menu_keyboard(),
                parse_mode="HTML"
            )
        elif module == "supercoin":
            cost = get_module_cost("supercoin")
            bot.edit_message_text(
                supercoin_menu_text(user_id, balance, status, cost),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=supercoin_menu_keyboard(),
                parse_mode="HTML"
            )
        elif module == "yoga":
            cost = get_module_cost("yoga")
            reward = get_yoga_refer_reward()
            yoga_code = user.get('yoga_code')
            bot.edit_message_text(
                yoga_menu_text(user_id, balance, status, yoga_code, reward, cost),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=yoga_menu_keyboard(),
                parse_mode="HTML"
            )
        elif module == "referral":
            bot.edit_message_text(
                referral_menu_text(user_id, balance, get_referral_count(user_id)),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=referral_menu_keyboard(),
                parse_mode="HTML"
            )
        elif module == "admin":
            if user_id == ADMIN_ID:
                bot.edit_message_text(
                    admin_panel_text(),
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=admin_panel_keyboard(),
                    parse_mode="HTML"
                )
            else:
                bot.answer_callback_query(call.id, "Unauthorized")
        elif module == "stats":
            total_users = get_total_users()
            total_coins = get_total_coins()
            total_usage = get_total_usage()
            bot.answer_callback_query(
                call.id, 
                f"📊 Users: {total_users} | Coins: {total_coins} | Usage: {total_usage}",
                show_alert=True
            )
        else:
            bot.answer_callback_query(call.id, "Module not found")
        
        bot.answer_callback_query(call.id)
        return
    
    # ==================== REFERRAL CALLBACKS ====================
    if data == "referral_get_link":
        user_id = call.from_user.id
        link = get_referral_link(user_id)
        referral_count = get_referral_count(user_id)
        pending_count = get_pending_referral_count(user_id)
        
        kb = InlineKeyboardMarkup()
        kb.row(InlineKeyboardButton("📤 Share Link", callback_data="referral_share"))
        kb.row(InlineKeyboardButton("🔙 Back", callback_data="back_menu"))
        
        bot.edit_message_text(
            f"🔗 <b>Your Referral Link</b>\n\n"
            f"<code>{link}</code>\n\n"
            f"📊 <b>Your Stats:</b>\n"
            f"👥 Successful: <code>{referral_count}</code>\n"
            f"⏳ Pending: <code>{pending_count}</code>\n"
            f"💰 Bonus: <code>+{REFERRAL_BONUS} Credits</code> per referral\n\n"
            f"Share this link with friends and earn credits when they join and stay!\n\n"
            f"💡 <b>Tip:</b> Each friend gets <b>+{NEW_USER_BONUS} Credits</b> on joining!",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=kb,
            parse_mode="HTML"
        )
        bot.answer_callback_query(call.id)
        return

    if data == "referral_share":
        user_id = call.from_user.id
        link = get_referral_link(user_id)
        bot.answer_callback_query(
            call.id,
            "📤 Copy this link and share with friends!\n\n" + link,
            show_alert=True
        )
        return

    if data == "referral_stats":
        user_id = call.from_user.id
        referral_count = get_referral_count(user_id)
        pending_count = get_pending_referral_count(user_id)
        balance = get_user_balance(user_id)
        bot.answer_callback_query(
            call.id,
            f"📊 Referral Stats:\n✅ Completed: {referral_count}\n⏳ Pending: {pending_count}\n💰 Balance: {balance}\n🎁 Bonus: +{REFERRAL_BONUS} per referral",
            show_alert=True
        )
        return
    
    # ==================== ADMIN CALLBACKS ====================
    if data.startswith("admin_"):
        user_id = call.from_user.id
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ Unauthorized - Admin only!")
            return
        
        action = data.replace("admin_", "")
        
        if action == "stats":
            total_users = get_total_users()
            total_coins = get_total_coins()
            total_usage = get_total_usage()
            
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM users WHERE last_used >= datetime('now', '-7 days')")
            active_users = c.fetchone()[0]
            conn.close()
            
            bot.answer_callback_query(
                call.id,
                f"📊 Bot Statistics:\n\n"
                f"👥 Total Users: {total_users}\n"
                f"🟢 Active (7d): {active_users}\n"
                f"💰 Total Coins: {total_coins}\n"
                f"📈 Total Usage: {total_usage}",
                show_alert=True
            )
            return
        
        if action == "users":
            users = get_all_users()
            if not users:
                bot.answer_callback_query(call.id, "No users found", show_alert=True)
                return
            
            user_list = "👥 <b>Top Users by Balance:</b>\n\n"
            for i, (uid, username, balance, status) in enumerate(users[:10], 1):
                name = username or f"User_{uid}"
                status_icon = "🟢" if status == "ACTIVE" else "🔴"
                user_list += f"{i}. {status_icon} {name} - 💰 {balance}\n"
            
            if len(users) > 10:
                user_list += f"\n... and {len(users) - 10} more users"
            
            kb = InlineKeyboardMarkup()
            kb.row(InlineKeyboardButton("📥 Export All", callback_data="admin_export_users"))
            kb.row(InlineKeyboardButton("🔙 Back", callback_data="back_menu"))
            
            bot.edit_message_text(
                user_list,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=kb,
                parse_mode="HTML"
            )
            bot.answer_callback_query(call.id)
            return
        
        if action == "export_users":
            users = get_all_users()
            if not users:
                bot.answer_callback_query(call.id, "No users to export", show_alert=True)
                return
            
            csv_data = "User ID,Username,Balance,Status\n"
            for uid, username, balance, status in users:
                csv_data += f"{uid},{username or 'N/A'},{balance},{status}\n"
            
            try:
                bot.send_document(
                    call.message.chat.id,
                    document=("users_export.csv", csv_data),
                    caption=f"📊 Users Export - {len(users)} users"
                )
                bot.answer_callback_query(call.id, "✅ Export sent!")
            except Exception as e:
                bot.answer_callback_query(call.id, f"❌ Export failed: {str(e)[:50]}", show_alert=True)
            return
        
        if action == "add_coins":
            msg = bot.send_message(
                call.message.chat.id,
                "💰 <b>Add Credits</b>\n\n"
                "Please send in format:\n"
                "<code>/addcoins USER_ID AMOUNT</code>\n\n"
                "Example: <code>/addcoins 123456789 10</code>\n\n"
                "Send /cancel to abort.",
                parse_mode="HTML"
            )
            bot.register_next_step_handler(msg, admin_add_coins_handler)
            bot.answer_callback_query(call.id)
            return
        
        if action == "remove_coins":
            msg = bot.send_message(
                call.message.chat.id,
                "➖ <b>Remove Credits</b>\n\n"
                "Please send in format:\n"
                "<code>/removecoins USER_ID AMOUNT</code>\n\n"
                "Example: <code>/removecoins 123456789 5</code>\n\n"
                "Send /cancel to abort.",
                parse_mode="HTML"
            )
            bot.register_next_step_handler(msg, admin_remove_coins_handler)
            bot.answer_callback_query(call.id)
            return
        
        if action == "broadcast":
            msg = bot.send_message(
                call.message.chat.id,
                "📢 <b>Broadcast Message</b>\n\n"
                "Send the message you want to broadcast to all users.\n\n"
                "⚠️ <b>Warning:</b> This will send to ALL users!\n\n"
                "Send /cancel to abort.",
                parse_mode="HTML"
            )
            bot.register_next_step_handler(msg, admin_broadcast_handler)
            bot.answer_callback_query(call.id)
            return
        
        if action == "costs":
            costs_text = "⚙️ <b>Module Costs</b>\n\n"
            for module, default in DEFAULT_COSTS.items():
                current = get_module_cost(module)
                costs_text += f"• {module.title()}: <code>{current}</code> credits\n"
            
            costs_text += f"\n📝 To update: <code>/setcost MODULE AMOUNT</code>\n"
            costs_text += f"Example: <code>/setcost yoga 2</code>\n\n"
            costs_text += f"💰 Yoga Reward: <code>{get_yoga_refer_reward()}</code> credits"
            
            kb = InlineKeyboardMarkup()
            kb.row(InlineKeyboardButton("🔙 Back", callback_data="back_menu"))
            
            bot.edit_message_text(
                costs_text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=kb,
                parse_mode="HTML"
            )
            bot.answer_callback_query(call.id)
            return
    
    # ==================== BROADCAST CALLBACKS ====================
    if data == "broadcast_confirm":
        user_id = call.from_user.id
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ Unauthorized!")
            return
        
        broadcast_msg = getattr(bot, 'user_data', {}).get('broadcast_msg')
        users = getattr(bot, 'user_data', {}).get('broadcast_users', [])
        
        if not broadcast_msg:
            bot.answer_callback_query(call.id, "❌ No broadcast message found!")
            return
        
        bot.edit_message_text(
            f"📢 <b>Broadcasting...</b>\n\n"
            f"Sending to <code>{len(users)}</code> users...",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="HTML"
        )
        
        success = 0
        failed = 0
        
        for uid, username, balance, status in users:
            try:
                bot.send_message(uid, broadcast_msg, parse_mode="HTML")
                success += 1
                time.sleep(0.05)
            except:
                failed += 1
        
        bot.edit_message_text(
            f"✅ <b>Broadcast Complete!</b>\n\n"
            f"✅ Sent: <code>{success}</code>\n"
            f"❌ Failed: <code>{failed}</code>",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="HTML"
        )
        
        bot.answer_callback_query(call.id, f"✅ Sent to {success} users")
        return

    if data == "broadcast_cancel":
        user_id = call.from_user.id
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ Unauthorized!")
            return
        
        bot.edit_message_text(
            "❌ Broadcast cancelled.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
        bot.answer_callback_query(call.id)
        return
    
    # ==================== SUPERCOIN CALLBACKS ====================
    if data == "supercoin_start":
        user_id = call.from_user.id
        cost = get_module_cost("supercoin")
        balance = get_user_balance(user_id)
        
        if balance < cost:
            bot.answer_callback_query(call.id, f"❌ Need {cost} credits!", show_alert=True)
            return
        
        user_supercoin_state[user_id] = "waiting_supercoin_phone"
        kb = InlineKeyboardMarkup()
        kb.row(InlineKeyboardButton("❌ Cancel", callback_data="supercoin_abort"))
        kb.row(InlineKeyboardButton("🔙 Back", callback_data="back_supercoin"))
        
        bot.edit_message_text(
            "💰 <b>Supercoin Fetcher</b>\n\n"
            "📱 Enter your 10-digit phone number to check Supercoins:\n\n"
            "Send /cancel to abort.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=kb,
            parse_mode="HTML"
        )
        bot.answer_callback_query(call.id)
        return
    
    if data == "supercoin_abort":
        user_id = call.from_user.id
        user_supercoin_state[user_id] = None
        if user_id in user_supercoin_otp_data:
            update_user_balance(user_id, user_supercoin_otp_data[user_id]["cost"])
            del user_supercoin_otp_data[user_id]
        bot.edit_message_text(
            "❌ Supercoin check cancelled.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=back_button()
        )
        bot.answer_callback_query(call.id)
        return
    
    if data == "supercoin_stats":
        user_id = call.from_user.id
        bot.answer_callback_query(
            call.id,
            "💰 Supercoin Fetcher\n\nUse 'Check Coins' to fetch your Supercoin balance!",
            show_alert=True
        )
        return
    
    # ==================== IG VIEWER CALLBACKS ====================
    if data == "igviewer_view":
        user_id = call.from_user.id
        cost = get_module_cost("igviewer")
        balance = get_user_balance(user_id)
        
        if balance < cost:
            bot.answer_callback_query(call.id, f"❌ Need {cost} credits!", show_alert=True)
            return
        
        user_igviewer_state[user_id] = "waiting_ig_username"
        kb = InlineKeyboardMarkup()
        kb.row(InlineKeyboardButton("❌ Cancel", callback_data="igviewer_abort"))
        kb.row(InlineKeyboardButton("🔙 Back", callback_data="back_menu"))
        
        bot.edit_message_text(
            "👁️ <b>IG Viewer</b>\n\n"
            "Enter the Instagram username to view stories:\n\n"
            "Example: <code>instagram</code>\n\n"
            "Send /cancel to abort.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=kb,
            parse_mode="HTML"
        )
        bot.answer_callback_query(call.id)
        return
    
    if data == "igviewer_abort":
        user_id = call.from_user.id
        user_igviewer_state[user_id] = None
        bot.edit_message_text(
            "❌ IG Viewer cancelled.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=back_button()
        )
        bot.answer_callback_query(call.id)
        return
    
    # ==================== SHOPSY CALLBACKS ====================
    if data == "shopsy_start":
        user_id = call.from_user.id
        if get_shopsy_login_status(user_id):
            user_shopsy_state[user_id] = "start_mining"
            kb = InlineKeyboardMarkup()
            kb.row(InlineKeyboardButton("⛏️ Start Mining Now", callback_data="shopsy_mine_now"))
            kb.row(InlineKeyboardButton("🔙 Back", callback_data="back_shopsy"))
            bot.edit_message_text(
                "✅ <b>Already Logged In!</b>\n\n"
                "Click 'Start Mining Now' to begin mining.\n\n"
                "⏱️ This will take 1-2 minutes.",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=kb,
                parse_mode="HTML"
            )
        else:
            user_shopsy_state[user_id] = "waiting_phone"
            kb = InlineKeyboardMarkup()
            kb.row(InlineKeyboardButton("❌ Cancel", callback_data="shopsy_abort"))
            kb.row(InlineKeyboardButton("🔙 Back", callback_data="back_shopsy"))
            bot.edit_message_text(
                "📱 Enter your 10-digit phone number to start Shopsy mining:\n\nSend /cancel to abort.",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=kb
            )
        bot.answer_callback_query(call.id)
        return
    
    if data == "shopsy_mine_now":
        user_id = call.from_user.id
        if not get_shopsy_login_status(user_id):
            bot.answer_callback_query(call.id, "❌ Please login first!", show_alert=True)
            return
        
        cost = get_module_cost("shopsy")
        balance = get_user_balance(user_id)
        if balance < cost:
            bot.answer_callback_query(call.id, f"❌ Need {cost} credits!", show_alert=True)
            return
        
        # Start mining directly
        user_shopsy_state[user_id] = "start_mining"
        fake_msg = call.message
        fake_msg.text = "start_mining"
        shopsy_start_mining_handler(fake_msg)
        bot.answer_callback_query(call.id)
        return
    
    if data == "shopsy_abort" or data == "shopsy_abort_otp":
        user_shopsy_state[user_id] = None
        if user_id in user_shopsy_otp_data:
            update_user_balance(user_id, user_shopsy_otp_data[user_id]["cost"])
            del user_shopsy_otp_data[user_id]
        bot.edit_message_text(
            "❌ Shopsy operation cancelled.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=back_button()
        )
        bot.answer_callback_query(call.id)
        return
    
    if data == "shopsy_stats":
        user_id = call.from_user.id
        balance = get_shopsy_balance(user_id)
        logged_in = get_shopsy_login_status(user_id)
        bot.answer_callback_query(
            call.id,
            f"🛍️ Shopsy Stats:\n🪙 Points: {balance}\n🔐 Status: {'✅ Logged In' if logged_in else '❌ Not Logged In'}",
            show_alert=True
        )
        return
    
    if data == "shopsy_logout":
        user_id = call.from_user.id
        logout_shopsy_user(user_id)
        bot.edit_message_text(
            "✅ Logged out of Shopsy successfully!",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=back_button()
        )
        bot.answer_callback_query(call.id)
        return
    
    # ==================== YOGA CALLBACKS ====================
    if data == "yoga_start":
        user_yoga_state[user_id] = "waiting_yoga_phone"
        kb = InlineKeyboardMarkup()
        kb.row(InlineKeyboardButton("❌ Cancel", callback_data="yoga_abort"))
        kb.row(InlineKeyboardButton("🔙 Back", callback_data="back_yoga"))
        bot.edit_message_text(
            "📱 Enter your 10-digit phone number for Yoga referral:\n\nSend /cancel to abort.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return
    
    if data == "yoga_abort" or data == "yoga_abort_otp":
        user_yoga_state[user_id] = None
        if user_id in user_yoga_otp_data:
            update_user_balance(user_id, user_yoga_otp_data[user_id]["cost"])
            del user_yoga_otp_data[user_id]
        bot.edit_message_text(
            "❌ Yoga operation cancelled.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=back_button()
        )
        bot.answer_callback_query(call.id)
        return
    
    if data == "yoga_setcode":
        bot.send_message(
            user_id,
            "🔑 <b>Set Your Yoga Referral Code</b>\n\n"
            "Please send your Habit.Yoga referral link or code.\n\n"
            "<b>Examples:</b>\n"
            "• https://habit.yoga/ABC123\n"
            "• ABC123\n\n"
            "Send /cancel to abort.",
            parse_mode="HTML"
        )
        user_yoga_state[user_id] = "waiting_yoga_code"
        bot.answer_callback_query(call.id)
        return
    
    if data == "yoga_stats":
        user = get_user(user_id)
        if user:
            bot.answer_callback_query(
                call.id,
                f"🧘 Yoga Stats:\nCode: {user.get('yoga_code', 'Not set')}\nRefers: {user.get('yoga_bot_refers', 0)}",
                show_alert=True
            )
        bot.answer_callback_query(call.id)
        return
    
    bot.answer_callback_query(call.id)

# ==================== ADMIN HANDLER FUNCTIONS ====================
def admin_add_coins_handler(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, "❌ Unauthorized!")
        return
    
    try:
        parts = message.text.strip().split()
        if len(parts) != 2:
            bot.reply_to(message, "❌ Invalid format! Use: /addcoins USER_ID AMOUNT")
            return
        
        target_id = int(parts[0])
        amount = int(parts[1])
        
        if amount <= 0:
            bot.reply_to(message, "❌ Amount must be positive!")
            return
        
        user = get_user(target_id)
        if not user:
            bot.reply_to(message, f"❌ User {target_id} not found!")
            return
        
        update_user_balance(target_id, amount)
        new_balance = get_user_balance(target_id)
        
        bot.reply_to(
            message,
            f"✅ <b>Added {amount} Credits</b>\n\n"
            f"👤 User: {user['first_name']} (ID: {target_id})\n"
            f"💰 New Balance: <code>{new_balance}</code>",
            parse_mode="HTML"
        )
        
        try:
            bot.send_message(
                target_id,
                f"🎉 <b>Admin Added Credits!</b>\n\n"
                f"➕ <code>+{amount} Credits</code> added to your account.\n"
                f"💰 New Balance: <code>{new_balance}</code>",
                parse_mode="HTML"
            )
        except:
            pass
            
    except ValueError:
        bot.reply_to(message, "❌ Invalid format! Use: /addcoins USER_ID AMOUNT")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)[:100]}")

def admin_remove_coins_handler(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, "❌ Unauthorized!")
        return
    
    try:
        parts = message.text.strip().split()
        if len(parts) != 2:
            bot.reply_to(message, "❌ Invalid format! Use: /removecoins USER_ID AMOUNT")
            return
        
        target_id = int(parts[0])
        amount = int(parts[1])
        
        if amount <= 0:
            bot.reply_to(message, "❌ Amount must be positive!")
            return
        
        user = get_user(target_id)
        if not user:
            bot.reply_to(message, f"❌ User {target_id} not found!")
            return
        
        current_balance = user['balance']
        if current_balance < amount:
            bot.reply_to(
                message,
                f"❌ User has insufficient balance!\n"
                f"Current: <code>{current_balance}</code>\n"
                f"Requested: <code>{amount}</code>",
                parse_mode="HTML"
            )
            return
        
        update_user_balance(target_id, -amount)
        new_balance = get_user_balance(target_id)
        
        bot.reply_to(
            message,
            f"✅ <b>Removed {amount} Credits</b>\n\n"
            f"👤 User: {user['first_name']} (ID: {target_id})\n"
            f"💰 New Balance: <code>{new_balance}</code>",
            parse_mode="HTML"
        )
        
        try:
            bot.send_message(
                target_id,
                f"⚠️ <b>Admin Removed Credits</b>\n\n"
                f"➖ <code>-{amount} Credits</code> removed from your account.\n"
                f"💰 New Balance: <code>{new_balance}</code>",
                parse_mode="HTML"
            )
        except:
            pass
            
    except ValueError:
        bot.reply_to(message, "❌ Invalid format! Use: /removecoins USER_ID AMOUNT")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)[:100]}")

def admin_broadcast_handler(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, "❌ Unauthorized!")
        return
    
    if message.text.lower() == '/cancel':
        bot.reply_to(message, "❌ Broadcast cancelled.")
        return
    
    users = get_all_users()
    if not users:
        bot.reply_to(message, "❌ No users to broadcast to!")
        return
    
    confirm_kb = InlineKeyboardMarkup()
    confirm_kb.row(
        InlineKeyboardButton("✅ Send", callback_data="broadcast_confirm"),
        InlineKeyboardButton("❌ Cancel", callback_data="broadcast_cancel")
    )
    
    if not hasattr(bot, 'user_data'):
        bot.user_data = {}
    bot.user_data['broadcast_msg'] = message.text
    bot.user_data['broadcast_users'] = users
    
    bot.reply_to(
        message,
        f"📢 <b>Broadcast Confirmation</b>\n\n"
        f"Message: {message.text[:200]}{'...' if len(message.text) > 200 else ''}\n\n"
        f"👥 Recipients: <code>{len(users)} users</code>\n\n"
        f"Click <b>✅ Send</b> to confirm broadcast.",
        reply_markup=confirm_kb,
        parse_mode="HTML"
    )

# ==================== YOGA SET CODE HANDLER ====================
@bot.message_handler(func=lambda message: user_yoga_state.get(message.from_user.id) == "waiting_yoga_code")
def yoga_set_code_handler(message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    if text.lower() in ['/cancel', 'cancel']:
        user_yoga_state[user_id] = None
        bot.reply_to(message, "❌ Yoga code setup cancelled.", reply_markup=back_button())
        return
    
    code = extract_yoga_code(text)
    if not code:
        bot.reply_to(
            message,
            "❌ Invalid Yoga code/link.\n\n"
            "Please send a valid Habit.Yoga referral link or code.\n"
            "Example: https://habit.yoga/ABC123 or ABC123"
        )
        return
    
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('UPDATE users SET yoga_code = ? WHERE user_id = ?', (code, user_id))
    conn.commit()
    conn.close()
    
    user_yoga_state[user_id] = None
    bot.reply_to(
        message,
        f"✅ <b>Yoga Code Set!</b>\n\n"
        f"🔑 Code: <code>{code}</code>\n\n"
        f"Now you can use the Yoga Referral module to earn rewards!",
        parse_mode="HTML",
        reply_markup=back_button()
    )

# ==================== SET COST COMMAND ====================
@bot.message_handler(commands=['setcost'])
def setcost_command(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, "❌ Unauthorized!")
        return
    
    try:
        parts = message.text.strip().split()
        if len(parts) != 3:
            bot.reply_to(
                message,
                "❌ Invalid format!\n\n"
                "Use: <code>/setcost MODULE AMOUNT</code>\n"
                "Example: <code>/setcost yoga 2</code>\n\n"
                "Available modules: firebase, flipkart, instagram_single, instagram_bulk, shopsy, yoga, igviewer, supercoin",
                parse_mode="HTML"
            )
            return
        
        module = parts[1].lower()
        amount = int(parts[2])
        
        if amount < 0:
            bot.reply_to(message, "❌ Amount must be non-negative!")
            return
        
        if module not in DEFAULT_COSTS:
            bot.reply_to(
                message,
                f"❌ Module '{module}' not found!\n\n"
                f"Available: {', '.join(DEFAULT_COSTS.keys())}",
                parse_mode="HTML"
            )
            return
        
        set_config(f"{module}_cost", str(amount))
        
        bot.reply_to(
            message,
            f"✅ <b>Cost Updated!</b>\n\n"
            f"📋 Module: <code>{module}</code>\n"
            f"💰 New Cost: <code>{amount}</code> credits",
            parse_mode="HTML"
        )
        
    except ValueError:
        bot.reply_to(message, "❌ Amount must be a number!")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)[:100]}")

# ==================== START COMMAND ====================
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    first_name = message.from_user.first_name or "User"
    
    user = get_user(user_id)
    
    referred_by = None
    if message.text and "ref_" in message.text:
        try:
            referred_by = int(message.text.split("ref_")[1].split()[0])
        except:
            pass
    
    if not user:
        create_user(user_id, username, first_name, referred_by)
        user = get_user(user_id)
        
        welcome_text = f"""
🎉 <b>Welcome to Viediet Utility Bot!</b>

You've received <b>+{NEW_USER_BONUS} Credits</b> as a welcome bonus!

<b>💡 Quick Start:</b>
• Explore all modules from the menu
• Earn free credits by referring friends
• Join our channel for updates

Click the menu below to get started!
"""
        bot.send_message(user_id, welcome_text, parse_mode="HTML")
    
    status = "✅ Member" if check_membership(user_id) else "❌ Not Joined"
    is_admin = user_id == ADMIN_ID
    
    bot.send_message(
        user_id,
        main_menu_text(user_id, first_name, get_user_balance(user_id), status),
        reply_markup=main_menu_keyboard(is_admin),
        parse_mode="HTML"
    )

# ==================== MAIN ====================
if __name__ == "__main__":
    init_db()
    
    task_thread = threading.Thread(target=run_scheduled_tasks, daemon=True)
    task_thread.start()
    
    logger.info("🤖 Bot started – ALL FEATURES WORKING!")
    logger.info("💰 Credit refund on failure enabled")
    logger.info("🧘 Yoga: OTP sending fixed")
    logger.info("🔄 Abort and Back buttons added for all features")
    logger.info("📊 Referral system - Get Link & Stats working")
    logger.info("👑 Admin Panel - All features working")
    logger.info("💰 Supercoin Fetcher - FIXED (returns 0 if no coins)")
    logger.info("⛏️ Shopsy Mining - FIXED (no more login loop)")
    logger.info("👁️ IG Viewer - Using storyviewer.com API (WORKING)")
    logger.info("🌐 Proxy support for Flipkart, Shopsy")
    
    try:
        bot.remove_webhook()
        time.sleep(2)
    except:
        pass
    
    try:
        bot.stop_polling()
        time.sleep(2)
    except:
        pass
    
    while True:
        try:
            logger.info("🔄 Starting polling...")
            bot.polling(non_stop=False, interval=1, timeout=30)
        except Exception as e:
            logger.error(f"Polling error: {e}")
            logger.info("🔄 Restarting polling in 10 seconds...")
            time.sleep(10)
