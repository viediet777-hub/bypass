#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

# ---- Import menu functions ----
from menu import (
    main_menu_text, main_menu_keyboard,
    firebase_menu_text, firebase_menu_keyboard,
    temp_menu_text, temp_menu_keyboard,
    flipkart_menu_text, flipkart_menu_keyboard,
    instagram_menu_text, instagram_menu_keyboard,
    referral_menu_text, referral_menu_keyboard,
    admin_panel_text, admin_panel_keyboard,
    music_menu_text, music_menu_keyboard,
    crownit_menu_text, crownit_menu_keyboard,
    shopsy_menu_text, shopsy_menu_keyboard
)

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

DEFAULT_COSTS = {
    "firebase": 1,
    "flipkart": 1,
    "instagram_single": 1,
    "instagram_bulk": 1,
    "crownit": 1,
    "shopsy": 1,
}

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
        shopsy_is_logged_in INTEGER DEFAULT 0
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
            'shopsy_is_logged_in': row[14] if len(row) > 14 else 0
        }
    return None

def create_user(user_id, username, first_name, referred_by=None, ip_address=None):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    now = datetime.now().isoformat()
    ref_code = f"REF{user_id}{random.randint(1000, 9999)}"
    c.execute('''INSERT OR IGNORE INTO users 
        (user_id, username, first_name, balance, status, registered_at, last_used, referred_by, referral_code, ip_address, shopsy_balance, shopsy_is_logged_in)
        VALUES (?, ?, ?, ?, 'ACTIVE', ?, ?, ?, ?, ?, 0, 0)''',
        (user_id, username, first_name, NEW_USER_BONUS, now, now, referred_by, ref_code, ip_address))
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

# ==================== SHOPSY SESSION FUNCTIONS (from so.py) ====================
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

# ==================== SHOPSY API FUNCTIONS (from so.py with fixes) ====================

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

# ==================== FIXED LOGIN WITH OTP (from so.py) ====================
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

# ==================== FIXED SESSION REFRESH (from so.py) ====================
async def refresh_session(session_data):
    """Refresh session - from so.py logic"""
    phone = session_data.get("phone")
    try:
        session_data = await run_sh_user_state(session_data)
        session_data["last_refresh"] = time.time()
        save_session(phone, session_data)
        return session_data
    except Exception as e:
        print(f"Session refresh error: {e}")
        return session_data

# ==================== FIXED CORE MINE LOGIC (from so.py) ====================
async def core_mine_logic(session_data, progress_callback=None):
    phone = session_data.get("phone")
    
    # 1. User state
    if progress_callback:
        await progress_callback("🔄 Fetching user state...")
    session_data = await run_sh_user_state(session_data)
    save_session(phone, session_data)

    # 2. Balance
    if progress_callback:
        await progress_callback("💰 Getting balance...")
    initial_user_data = await get_user_info_tg(session_data)
    if not initial_user_data:
        return {"status": "fail", "earned": 0, "msg": "Session expired. Please re-login."}
    
    initial_coins = initial_user_data.get("earnings", {}).get("coinsEarnedTotal", 0)

    # 3. Gullak
    if progress_callback:
        await progress_callback("🎁 Claiming gullak...")
    await claim_gullak_tg(session_data)

    # 4. Games
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
        
        # Refresh session before each game (from so.py)
        session_data = await refresh_session(session_data)
        if not session_data.get("isLoggedIn"):
            return {"status": "fail", "earned": 0, "msg": "Session expired. Please re-login."}
        
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

    # 5. Final
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
    if not phone.isdigit() or len(phone) != 10:
        bot.reply_to(message, "❌ Please enter exactly 10 digits.")
        return
    
    cost = get_module_cost("shopsy")
    balance = get_user_balance(user_id)
    if balance < cost:
        bot.reply_to(message, f"❌ Insufficient credits! You need {cost} credits. Your balance: {balance}")
        return
    
    update_user_balance(user_id, -cost)
    
    status_msg = bot.reply_to(message, f"📱 Sending OTP to +91{phone}...")
    
    def send_otp_thread():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            session_data, msg = loop.run_until_complete(login_with_otp(phone))
            loop.close()
            
            if not session_data:
                update_user_balance(user_id, cost)
                bot.edit_message_text(f"❌ Failed: {msg}", chat_id=message.chat.id, message_id=status_msg.message_id)
                user_shopsy_state[user_id] = None
                return
            
            user_shopsy_otp_data[user_id] = {"session_data": session_data, "phone": phone}
            user_shopsy_state[user_id] = "waiting_otp"
            bot.edit_message_text(
                f"✅ OTP sent to +91{phone}!\n\n"
                f"Enter the OTP code you received:",
                chat_id=message.chat.id,
                message_id=status_msg.message_id
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
    if not otp.isdigit():
        bot.reply_to(message, "❌ Enter a valid OTP.")
        return
    
    data = user_shopsy_otp_data.get(user_id)
    if not data:
        bot.reply_to(message, "❌ Session expired. Start over.")
        user_shopsy_state[user_id] = None
        return
    
    session_data = data["session_data"]
    phone = data["phone"]
    
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
                cost = get_module_cost("shopsy")
                update_user_balance(user_id, cost)
                bot.edit_message_text(
                    "❌ Invalid OTP. Credits refunded. Please try again with /shopsy",
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id
                )
                user_shopsy_state[user_id] = None
                user_shopsy_otp_data.pop(user_id, None)
        except Exception as e:
            cost = get_module_cost("shopsy")
            update_user_balance(user_id, cost)
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
                update_user_balance(user_id, cost)
                bot.edit_message_text(
                    f"❌ **Shopsy Mining Failed**\n\n{result.get('msg', 'Unknown error')}\n\nCredits refunded.",
                    chat_id=message.chat.id,
                    message_id=progress_msg.message_id
                )
            
            user_shopsy_state[user_id] = None
            user_shopsy_otp_data.pop(user_id, None)
            
        except Exception as e:
            cost = get_module_cost("shopsy")
            update_user_balance(user_id, cost)
            bot.edit_message_text(f"❌ Error: {str(e)[:200]}", chat_id=message.chat.id, message_id=progress_msg.message_id)
            user_shopsy_state[user_id] = None
            user_shopsy_otp_data.pop(user_id, None)
    
    threading.Thread(target=mine_thread).start()

# ==================== SHOPSY CALLBACK HANDLER ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith("shopsy_"))
def handle_shopsy_callback(call):
    user_id = call.from_user.id
    action = call.data.split("_")[1]
    
    if action == "start":
        cost = get_module_cost("shopsy")
        balance = get_user_balance(user_id)
        if balance < cost:
            bot.answer_callback_query(call.id, f"❌ You need {cost} credits for Shopsy mining!", show_alert=True)
            return
        
        user_shopsy_state[user_id] = "waiting_phone"
        bot.answer_callback_query(call.id, "📱 Enter your phone number")
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
        
        bot.answer_callback_query(call.id, "📊 Fetching stats...")
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
        bot.answer_callback_query(call.id, "✅ Logged out from Shopsy!")
        bot.edit_message_text(
            "🚪 **Logged out from Shopsy**\n\n"
            "Your Shopsy session has been cleared.\n"
            "You can login again anytime.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=shopsy_menu_keyboard(),
            parse_mode="HTML"
        )

# ==================== REST OF THE BOT CODE (TEMP MAIL, FLIPKART, INSTAGRAM, APK, CROWNIT, MUSIC, ETC.) ====================
# ... (keep all your existing code for temp mail, flipkart, instagram, apk, crownit, music handlers)

# ==================== MAIN ====================
if __name__ == "__main__":
    init_db()
    task_thread = threading.Thread(target=run_scheduled_tasks, daemon=True)
    task_thread.start()
    logger.info("🤖 Bot started – Shopsy Mining fixed with so.py session logic!")
    
    # Fix for 409 Conflict - remove webhook
    try:
        bot.remove_webhook()
        time.sleep(1)
    except:
        pass
    
    # Simple polling
    while True:
        try:
            bot.polling(non_stop=False, interval=1, timeout=30)
        except Exception as e:
            logger.error(f"Polling error: {e}")
            time.sleep(5)
