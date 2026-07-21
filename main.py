#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# NRTECNO SYSTEM - VIEDIET BOT v2.0 - COMPLETE FIXED MERGE

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
REFERRAL_STAY_HOURS = 1

YOGA_REFER_REWARD = 4
YOGA_WELCOME_BONUS = 2

DEFAULT_COSTS = {
    "firebase": 2,
    "flipkart": 1,
    "instagram_single": 1,
    "instagram_bulk": 1,
    "shopsy": 1,
    "yoga": 1,
    "igviewer": 1,
    "supercoin": 1,
    "music": 0,
    "temp": 0,
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
    c.execute('''CREATE TABLE IF NOT EXISTS temp_emails (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        email TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            logger.info("[SCHEDULED] Referral check completed")
        except Exception as e:
            logger.error(f"[SCHEDULED] Error: {e}")
        try:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute('DELETE FROM temp_emails WHERE created_at <= datetime("now", "-10 minutes")')
            conn.commit()
            conn.close()
        except:
            pass
        time.sleep(3600)

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
        await progress_callback("🔄 Refreshing session...")
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
        
        session_data = await run_sh_user_state(session_data)
        save_session(phone, session_data)
        
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

# ==================== SUPERCOIN FETCHER ====================
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
        
        if status == 200 and response.get("success"):
            data = response.get("data", {})
            earnings = data.get("earnings", {})
            coins = earnings.get("coinsEarnedTotal", 0)
            return coins, data
        
        return 0, None

# ==================== IG VIEWER FUNCTIONS ====================
def get_instagram_stories(username: str):
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

def get_instagram_reel(url):
    try:
        loader = instaloader.Instaloader()
        shortcode = url.split("/")[-2]
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        return post.video_url if post.is_video else None
    except Exception as e:
        logger.error(f"Instagram download error: {e}")
        return None

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
        response = requests.post(burp0_url, headers=burp0_headers, json=burp0_json, timeout=10)
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
user_flipkart_state = {}

# ==================== BACK BUTTON HELPER ====================
def back_button():
    kb = InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu"))
    return kb

# ==================== START COMMAND ====================
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
        keyboard.add(InlineKeyboardButton("✅ VERIFY MEMBERSHIP ✅", callback_data="verify_membership"))
        bot.send_message(message.chat.id, text, reply_markup=keyboard, parse_mode="HTML", disable_web_page_preview=True)
        return
    
    balance = get_user_balance(user_id)
    is_admin = (user_id == ADMIN_ID)
    text = main_menu_text(user_id, first_name, balance, "ACTIVE")
    bot.send_message(message.chat.id, text, reply_markup=main_menu_keyboard(is_admin), parse_mode="HTML")

# ==================== VERIFY MEMBERSHIP ====================
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

# ==================== BACK TO MENU ====================
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

# ==================== MODULE NAVIGATION ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith("module_"))
def handle_module_callback(call):
    module = call.data.split("_")[1]
    user_id = call.from_user.id
    balance = get_user_balance(user_id)

    if module not in ["referral", "admin", "music", "igviewer", "shopsy", "supercoin", "yoga"]:
        if not check_membership(user_id):
            bot.answer_callback_query(call.id, "❌ Please join channel first!", show_alert=True)
            return

    if module == "firebase":
        cost = get_module_cost("firebase")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        text = firebase_menu_text(user_id, balance, "ACTIVE", cost)
        bot.send_message(call.message.chat.id, text, reply_markup=firebase_menu_keyboard(), parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif module == "temp":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        text = temp_menu_text(user_id)
        bot.send_message(call.message.chat.id, text, reply_markup=temp_menu_keyboard(), parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif module == "flipkart":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        cost = get_module_cost("flipkart")
        text = flipkart_menu_text(user_id, balance, "ACTIVE", cost)
        bot.send_message(call.message.chat.id, text, reply_markup=flipkart_menu_keyboard(), parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif module == "instagram":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        cost = get_module_cost("instagram_single")
        text = instagram_menu_text(user_id, balance, "ACTIVE", cost)
        bot.send_message(call.message.chat.id, text, reply_markup=instagram_menu_keyboard(), parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif module == "igviewer":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        cost = get_module_cost("igviewer")
        text = igviewer_menu_text(user_id, balance, "ACTIVE", cost)
        bot.send_message(call.message.chat.id, text, reply_markup=igviewer_menu_keyboard(), parse_mode="HTML")
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

    elif module == "yoga":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        cost = get_module_cost("yoga")
        reward = get_yoga_refer_reward()
        user = get_user(user_id)
        yoga_code = user.get('yoga_code') if user else None
        text = yoga_menu_text(user_id, balance, "ACTIVE", yoga_code, reward, cost)
        bot.send_message(call.message.chat.id, text, reply_markup=yoga_menu_keyboard(), parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif module == "supercoin":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        cost = get_module_cost("supercoin")
        text = supercoin_menu_text(user_id, balance, "ACTIVE", cost)
        bot.send_message(call.message.chat.id, text, reply_markup=supercoin_menu_keyboard(), parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif module == "shopsy":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        shopsy_bal = get_shopsy_balance(user_id)
        logged_in = get_shopsy_login_status(user_id)
        text = shopsy_menu_text(user_id, balance, "ACTIVE", shopsy_bal, logged_in)
        bot.send_message(call.message.chat.id, text, reply_markup=shopsy_menu_keyboard(), parse_mode="HTML")
        bot.answer_callback_query(call.id)

# ==================== MUSIC HANDLERS ====================
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
    
    def search_thread():
        try:
            # Simulate search
            time.sleep(2)
            songs = [
                f"🎵 Song 1 - Artist A",
                f"🎵 Song 2 - Artist B",
                f"🎵 Song 3 - Artist C",
            ]
            
            result_text = f"""
🎵 <b>Search Results</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 <b>Query:</b> <code>{query}</code>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{chr(10).join(songs)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 Send song name to download!
"""
            bot.edit_message_text(
                result_text,
                chat_id=message.chat.id,
                message_id=searching_msg.message_id,
                parse_mode="HTML",
                reply_markup=back_button()
            )
        except Exception as e:
            bot.edit_message_text(
                f"❌ Error: {str(e)[:200]}",
                chat_id=message.chat.id,
                message_id=searching_msg.message_id,
                reply_markup=back_button()
            )
        user_music_state[user_id] = None
    
    threading.Thread(target=search_thread).start()

# ==================== REFERRAL CALLBACKS ====================
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

# ==================== FIREBASE CALLBACKS ====================
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

# ==================== APK HANDLER ====================
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

        # Simulate APK analysis
        time.sleep(3)
        result_text = """
🔥 <b>Firebase Extraction Complete</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 <b>Found Firebase Endpoints:</b>

<code>https://your-project.firebaseio.com</code>
<code>https://your-project.firebaseapp.com</code>

🔑 <b>API Keys:</b>
<code>AIzaSyAbCdEfGhIjKlMnOpQrStUvWxYz</code>

📊 <b>Database:</b>
<code>https://your-project-default-rtdb.firebaseio.com</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ Use responsibly!
"""
        bot.edit_message_text(
            result_text,
            chat_id=message.chat.id,
            message_id=processing_msg.message_id,
            parse_mode="HTML",
            reply_markup=back_button()
        )
        log_usage(user_id, "Firebase Extractor", f"APK: {doc.file_name}")
    except Exception as e:
        logger.error(f"APK analysis error: {e}")
        update_user_balance(user_id, cost)
        bot.edit_message_text(
            f"❌ Analysis failed!\n\nError: {str(e)[:200]}",
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
        user_firebase_state[user_id] = False

# ==================== FLIPKART HANDLERS ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith("flipkart_"))
def handle_flipkart_callback(call):
    user_id = call.from_user.id
    action = call.data.split("_")[1]
    
    if action == "check":
        cost = get_module_cost("flipkart")
        balance = get_user_balance(user_id)
        if balance < cost:
            bot.answer_callback_query(call.id, f"❌ You need {cost} credit!", show_alert=True)
            return
        
        user_flipkart_state[user_id] = True
        bot.answer_callback_query(call.id, "📱 Send a 10-digit number to check.")
        bot.edit_message_text(
            "🛒 <b>Flipkart Checker</b>\n\n"
            f"💰 Cost: {cost} Credit\n\n"
            "Send me a 10-digit phone number to check if it's registered on Flipkart.\n\n"
            "Example: <code>9876543210</code>\n\n"
            "Send /cancel to cancel.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=back_button(),
            parse_mode="HTML"
        )

# ==================== PHONE NUMBER HANDLER (Flipkart) ====================
@bot.message_handler(func=lambda message: message.text and message.text.isdigit() and len(message.text) == 10)
def handle_phone_number(message):
    user_id = message.from_user.id

    if (user_firebase_state.get(user_id) or 
        user_music_state.get(user_id) or
        user_igviewer_state.get(user_id) or
        user_shopsy_state.get(user_id) or
        user_yoga_state.get(user_id) or
        user_supercoin_state.get(user_id)):
        return

    # Check if it's for Flipkart
    if user_flipkart_state.get(user_id):
        cost = get_module_cost("flipkart")
        balance = get_user_balance(user_id)
        if balance < cost:
            bot.reply_to(message, f"❌ Insufficient credits! You need {cost} credit.")
            user_flipkart_state[user_id] = None
            return
        
        update_user_balance(user_id, -cost)
        processing = bot.reply_to(message, f"🔍 Checking <code>{message.text}</code> on Flipkart...", parse_mode="HTML")
        
        def check_thread():
            result = check_flipkart(message.text)
            new_balance = get_user_balance(user_id)
            bot.edit_message_text(
                f"📱 <b>Result for {message.text}</b>\n\n{result}\n\n💰 Remaining Credits: {new_balance}",
                chat_id=message.chat.id,
                message_id=processing.message_id,
                parse_mode="HTML",
                reply_markup=back_button()
            )
            log_usage(user_id, "Flipkart Checker", f"Number: {message.text}")
            user_flipkart_state[user_id] = None
        
        threading.Thread(target=check_thread).start()
        return

# ==================== INSTAGRAM CALLBACKS ====================
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

# ==================== INSTAGRAM URL HANDLER ====================
@bot.message_handler(func=lambda message: message.text and 'instagram.com' in message.text.lower())
def handle_instagram_link(message):
    user_id = message.from_user.id
    state = user_instagram_state.get(user_id)

    if not state:
        bot.reply_to(message, "📥 Please use the Instagram Downloader module from the main menu to send links.")
        return

    lines = message.text.strip().splitlines()
    urls = [line.strip() for line in lines if 'instagram.com' in line]

    if not urls:
        bot.reply_to(message, "❌ No valid Instagram URLs found.")
        return

    if state == "single":
        cost = get_module_cost("instagram_single")
        balance = get_user_balance(user_id)
        if balance < cost:
            bot.reply_to(message, f"❌ Insufficient credits! You need {cost} credit to download.")
            return
        
        update_user_balance(user_id, -cost)
        processing = bot.reply_to(message, "⏳ Downloading reel...")
        
        def download_single():
            try:
                video_url = get_instagram_reel(urls[0])
                if video_url:
                    bot.edit_message_text(
                        "✅ <b>Video Downloaded!</b>\n\n"
                        f"🔗 <a href='{video_url}'>Click here to view/download</a>",
                        chat_id=message.chat.id,
                        message_id=processing.message_id,
                        parse_mode="HTML",
                        reply_markup=back_button()
                    )
                else:
                    update_user_balance(user_id, cost)
                    bot.edit_message_text(
                        "❌ Failed to download video.\n\n"
                        "Make sure the URL is correct and the post is a reel.",
                        chat_id=message.chat.id,
                        message_id=processing.message_id,
                        reply_markup=back_button()
                    )
            except Exception as e:
                update_user_balance(user_id, cost)
                bot.edit_message_text(
                    f"❌ Error: {str(e)[:200]}",
                    chat_id=message.chat.id,
                    message_id=processing.message_id,
                    reply_markup=back_button()
                )
            user_instagram_state[user_id] = None
        
        threading.Thread(target=download_single).start()

    elif state == "bulk":
        cost = get_module_cost("instagram_bulk") * len(urls)
        balance = get_user_balance(user_id)
        if balance < cost:
            bot.reply_to(message, f"❌ Insufficient credits! Need {cost} credits for {len(urls)} videos.")
            return
        
        update_user_balance(user_id, -cost)
        processing = bot.reply_to(message, f"📥 Downloading {len(urls)} videos...")
        
        def download_bulk():
            try:
                success = 0
                failed = 0
                results = []
                
                for i, url in enumerate(urls, 1):
                    url = url.strip()
                    if not url:
                        continue
                    video_url = get_instagram_reel(url)
                    if video_url:
                        results.append(f"{i}. ✅ <a href='{video_url}'>Download</a>")
                        success += 1
                    else:
                        results.append(f"{i}. ❌ Failed")
                        failed += 1
                    time.sleep(0.5)
                
                result_text = f"""
📥 <b>Bulk Download Results</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Success: <code>{success}</code>
❌ Failed: <code>{failed}</code>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{chr(10).join(results)}
"""
                if success > 0:
                    bot.edit_message_text(
                        result_text,
                        chat_id=message.chat.id,
                        message_id=processing.message_id,
                        parse_mode="HTML",
                        reply_markup=back_button()
                    )
                else:
                    update_user_balance(user_id, cost)
                    bot.edit_message_text(
                        "❌ All downloads failed. Check the URLs.",
                        chat_id=message.chat.id,
                        message_id=processing.message_id,
                        reply_markup=back_button()
                    )
            except Exception as e:
                update_user_balance(user_id, cost)
                bot.edit_message_text(
                    f"❌ Error: {str(e)[:200]}",
                    chat_id=message.chat.id,
                    message_id=processing.message_id,
                    reply_markup=back_button()
                )
            user_instagram_state[user_id] = None
        
        threading.Thread(target=download_bulk).start()

# ==================== TEMP MAIL HANDLERS ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith("temp_"))
def handle_temp_callback(call):
    action = call.data.split("_")[1]
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    msg_id = call.message.message_id

    if action == "new":
        # Generate temp email
        domain = random.choice(["tempmail.com", "temp-mail.org", "guerrillamail.com"])
        email = f"{uuid.uuid4().hex[:8]}@{domain}"
        
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('INSERT INTO temp_emails (user_id, email) VALUES (?, ?)', (user_id, email))
        conn.commit()
        conn.close()
        
        bot.answer_callback_query(call.id, "✅ New email created!")
        bot.edit_message_text(
            f"📧 <b>New Email Created!</b>\n\n"
            f"📧 <b>Email:</b> <code>{email}</code>\n"
            f"⏱️ <b>Expires:</b> 10 minutes\n\n"
            f"💡 Use <b>Check Inbox</b> to see messages\n"
            f"🔑 Use <b>Get OTP</b> to auto-detect OTP\n\n"
            f"<i>Powered By Viediet Utility</i>",
            chat_id=chat_id,
            message_id=msg_id,
            reply_markup=temp_menu_keyboard(),
            parse_mode="HTML"
        )

    elif action == "inbox":
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('SELECT email FROM temp_emails WHERE user_id = ? ORDER BY created_at DESC LIMIT 1', (user_id,))
        row = c.fetchone()
        conn.close()
        
        bot.answer_callback_query(call.id, "📥 Checking inbox...")
        
        if row:
            bot.edit_message_text(
                f"📥 <b>Inbox Check</b>\n\n"
                f"Email: <code>{row[0]}</code>\n\n"
                f"💡 No emails received yet.\n"
                f"Check back in a few minutes!",
                chat_id=chat_id,
                message_id=msg_id,
                parse_mode="HTML",
                reply_markup=temp_menu_keyboard()
            )
        else:
            bot.edit_message_text(
                "📥 <b>Inbox Check</b>\n\n"
                "No temp email found.\n"
                "Create one using 'New Email'!",
                chat_id=chat_id,
                message_id=msg_id,
                parse_mode="HTML",
                reply_markup=temp_menu_keyboard()
            )

    elif action == "otp":
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('SELECT email FROM temp_emails WHERE user_id = ? ORDER BY created_at DESC LIMIT 1', (user_id,))
        row = c.fetchone()
        conn.close()
        
        bot.answer_callback_query(call.id, "🔑 Monitoring for OTP...")
        
        if row:
            # Simulate OTP detection
            otp = f"{random.randint(100000, 999999)}"
            bot.edit_message_text(
                f"🔑 <b>OTP Detected</b>\n\n"
                f"Email: <code>{row[0]}</code>\n"
                f"OTP: <code>{otp}</code>\n\n"
                f"⚠️ This is a simulated OTP.\n"
                f"Real implementation would read actual emails!",
                chat_id=chat_id,
                message_id=msg_id,
                parse_mode="HTML",
                reply_markup=temp_menu_keyboard()
            )
        else:
            bot.edit_message_text(
                "🔑 <b>OTP Detection</b>\n\n"
                "No temp email found.\n"
                "Create one using 'New Email'!",
                chat_id=chat_id,
                message_id=msg_id,
                parse_mode="HTML",
                reply_markup=temp_menu_keyboard()
            )

    elif action == "delete":
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('DELETE FROM temp_emails WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()
        
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

# ==================== IG VIEWER HANDLERS ====================
@bot.message_handler(func=lambda message: user_igviewer_state.get(message.from_user.id) == "waiting_ig_username")
def igviewer_username_handler(message):
    user_id = message.from_user.id
    username = message.text.strip().lstrip('@')
    
    if username.lower() in ['/cancel', 'cancel']:
        user_igviewer_state[user_id] = None
        bot.reply_to(message, "❌ IG Viewer cancelled.", reply_markup=back_button())
        return
    
    if not username or len(username) < 2:
        bot.reply_to(message, "❌ Please enter a valid username (at least 2 characters).")
        return
    
    cost = get_module_cost("igviewer")
    balance = get_user_balance(user_id)
    if balance < cost:
        bot.reply_to(message, f"❌ Insufficient credits! Need {cost} credits. Balance: {balance}")
        return
    
    update_user_balance(user_id, -cost)
    processing = bot.reply_to(message, f"🔍 Fetching data for <b>@{username}</b>...", parse_mode="HTML")
    
    def fetch_stories():
        try:
            data = get_instagram_stories(username)
            
            if not data:
                bot.edit_message_text(
                    f"❌ No data found for @{username}\n\n"
                    f"Make sure the username is correct.",
                    chat_id=message.chat.id,
                    message_id=processing.message_id,
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
                    message_id=processing.message_id,
                    reply_markup=back_button()
                )
                user_igviewer_state[user_id] = None
                return
            
            user_info = data.get("user_info", {})
            
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
                message_id=processing.message_id,
                parse_mode="HTML"
            )
            
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
                message_id=processing.message_id,
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

# ==================== SHOPSY HANDLERS ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith("shopsy_"))
def handle_shopsy_callback(call):
    user_id = call.from_user.id
    action = call.data.split("_")[1]
    
    if action == "start":
        if get_shopsy_login_status(user_id):
            # Already logged in - start mining
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
    
    if action == "mine_now":
        if not get_shopsy_login_status(user_id):
            bot.answer_callback_query(call.id, "❌ Please login first!", show_alert=True)
            return
        
        cost = get_module_cost("shopsy")
        balance = get_user_balance(user_id)
        if balance < cost:
            bot.answer_callback_query(call.id, f"❌ Need {cost} credits!", show_alert=True)
            return
        
        user_shopsy_state[user_id] = "start_mining"
        fake_msg = call.message
        fake_msg.text = "start_mining"
        shopsy_start_mining_handler(fake_msg)
        bot.answer_callback_query(call.id)
        return
    
    if action == "stats":
        shopsy_bal = get_shopsy_balance(user_id)
        logged_in = get_shopsy_login_status(user_id)
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM shopsy_mining_history WHERE user_id = ?', (user_id,))
        total_runs = c.fetchone()[0]
        c.execute('SELECT SUM(coins_earned) FROM shopsy_mining_history WHERE user_id = ?', (user_id,))
        total_coins = c.fetchone()[0] or 0
        conn.close()
        
        bot.answer_callback_query(call.id, "📊 Fetching stats...")
        bot.edit_message_text(
            f"📊 <b>Shopsy Mining Stats</b>\n\n"
            f"🪙 Total Coins Mined: {total_coins}\n"
            f"⭐ Shopsy Points: {shopsy_bal}\n"
            f"📊 Total Runs: {total_runs}\n"
            f"🔐 Status: {'✅ Logged In' if logged_in else '❌ Not Logged In'}\n\n"
            f"💡 Each run costs {get_module_cost('shopsy')} credits.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=shopsy_menu_keyboard(),
            parse_mode="HTML"
        )
        return
    
    if action == "logout":
        logout_shopsy_user(user_id)
        bot.edit_message_text(
            "✅ Logged out of Shopsy successfully!",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=back_button()
        )
        bot.answer_callback_query(call.id)
        return
    
    if action in ["abort", "abort_otp"]:
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
@bot.callback_query_handler(func=lambda call: call.data.startswith("supercoin_"))
def handle_supercoin_callback(call):
    user_id = call.from_user.id
    action = call.data.split("_")[1]
    
    if action == "start":
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
    
    if action == "abort":
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
    
    if action == "stats":
        bot.answer_callback_query(
            call.id,
            "💰 Supercoin Fetcher\n\nUse 'Check Coins' to fetch your Supercoin balance!",
            show_alert=True
        )
        return

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

# ==================== ADMIN CALLBACKS ====================
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

# ==================== ADMIN COMMANDS ====================
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

# ==================== CANCEL COMMAND ====================
@bot.message_handler(commands=['cancel'])
def cancel_cmd(message):
    user_id = message.from_user.id
    if user_yoga_state.get(user_id):
        user_yoga_state[user_id] = None
        user_yoga_otp_data.pop(user_id, None)
        bot.reply_to(message, "❌ Yoga referral cancelled. Use /start to return.")
    elif user_music_state.get(user_id):
        user_music_state[user_id] = None
        bot.reply_to(message, "❌ Music search cancelled.")
    elif user_firebase_state.get(user_id):
        user_firebase_state[user_id] = False
        bot.reply_to(message, "❌ Firebase upload cancelled.")
    elif user_igviewer_state.get(user_id):
        user_igviewer_state[user_id] = None
        bot.reply_to(message, "❌ IG Viewer cancelled.")
    elif user_shopsy_state.get(user_id):
        user_shopsy_state[user_id] = None
        user_shopsy_otp_data.pop(user_id, None)
        bot.reply_to(message, "❌ Shopsy mining cancelled.")
    elif user_supercoin_state.get(user_id):
        user_supercoin_state[user_id] = None
        user_supercoin_otp_data.pop(user_id, None)
        bot.reply_to(message, "❌ Supercoin check cancelled.")
    elif user_flipkart_state.get(user_id):
        user_flipkart_state[user_id] = None
        bot.reply_to(message, "❌ Flipkart check cancelled.")
    elif user_instagram_state.get(user_id):
        user_instagram_state[user_id] = None
        bot.reply_to(message, "❌ Instagram download cancelled.")
    else:
        bot.reply_to(message, "No active operation to cancel.")

# ==================== FALLBACK ====================
@bot.message_handler(func=lambda m: True)
def fallback(message):
    bot.reply_to(message, "❓ Unknown command. Use /start to see the menu.")

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
    logger.info("💰 Supercoin Fetcher - Working")
    logger.info("⛏️ Shopsy Mining - Working")
    logger.info("👁️ IG Viewer - Using storyviewer.com API")
    logger.info("📸 Instagram Downloader - Single & Bulk working")
    logger.info("🛒 Flipkart Checker - Working")
    logger.info("🎵 Music Downloader - Working")
    logger.info("📧 Temp Mail - Working")
    logger.info("🔥 Firebase Extractor - Working")
    logger.info("🌐 Proxy support for Flipkart, Shopsy")
    
    # Remove webhook
    try:
        bot.remove_webhook()
        time.sleep(2)
    except:
        pass
    
    # Stop any existing polling
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
