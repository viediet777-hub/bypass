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
from datetime import datetime, timedelta
from menu import (
    main_menu_text, main_menu_keyboard,
    shopsy_menu_text, shopsy_menu_keyboard,
    firebase_menu_text, firebase_menu_keyboard,
    temp_menu_text, temp_menu_keyboard,
    flipkart_menu_text, flipkart_menu_keyboard,
    instagram_menu_text, instagram_menu_keyboard,
    referral_menu_text, referral_menu_keyboard,
    admin_panel_text, admin_panel_keyboard
)
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ---- Import Shopsy module ----
import shopsy

# ==================== CONFIG ====================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    logging.error("BOT_TOKEN environment variable not set.")
    exit(1)

ADMIN_ID = int(os.environ.get("ADMIN_ID", 1364476174))
CHANNEL_USERNAME = "viedietlooters"
GROUP_USERNAME = "viedietlooterschat"
REFERRAL_BONUS = 1
NEW_USER_BONUS = 10
MIN_ACCOUNT_AGE_DAYS = 7
REFERRAL_STAY_HOURS = 0

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

DB_PATH = "viediet_bot.db"

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
        shopsy_balance INTEGER DEFAULT 0
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
            'last_check': row[12],
            'shopsy_balance': row[13] if len(row) > 13 else 0
        }
    return None

def create_user(user_id, username, first_name, referred_by=None, ip_address=None):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    now = datetime.now().isoformat()
    ref_code = f"REF{user_id}{random.randint(1000, 9999)}"
    c.execute('''INSERT OR IGNORE INTO users 
        (user_id, username, first_name, balance, status, registered_at, last_used, referred_by, referral_code, ip_address, shopsy_balance)
        VALUES (?, ?, ?, ?, 'ACTIVE', ?, ?, ?, ?, ?, 0)''',
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

def update_shopsy_balance(user_id, delta):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('UPDATE users SET shopsy_balance = shopsy_balance + ? WHERE user_id = ?', (delta, user_id))
    conn.commit()
    conn.close()

def get_shopsy_balance(user_id):
    user = get_user(user_id)
    return user['shopsy_balance'] if user else 0

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
                group_member = bot.get_chat_member(f"@{GROUP_USERNAME}", referred_id)
                if channel_member.status in ['member', 'administrator', 'creator'] and \
                   group_member.status in ['member', 'administrator', 'creator']:
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

def is_channel_member(user_id):
    try:
        member = bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

def is_group_member(user_id):
    try:
        member = bot.get_chat_member(f"@{GROUP_USERNAME}", user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

def check_membership(user_id):
    return is_channel_member(user_id) and is_group_member(user_id)

# ==================== GLOBAL STATES ====================
user_temp_sessions = {}
user_instagram_state = {}
user_firebase_state = {}
pending_purchases = {}
user_buy_state = {}
user_music_state = {}
user_shopsy_state = {}   # user_id -> "waiting_phone" / "waiting_otp" / None
shopsy_temp_data = {}    # user_id -> { 'phone': ..., 'session_data': ..., 'mining_thread': ... }

# ---------- NEW: Session Extractor states ----------
user_session_state = {}      # user_id -> "waiting_phone" / "waiting_otp" / None
session_temp_data = {}       # user_id -> { 'phone': ..., 'session_data': ..., 'req_id': ... }

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
            f"You must join our communities to use this bot.\n\n"
            f"📢 <b>Required Channels:</b>\n"
            f"• Channel: <a href='https://t.me/{CHANNEL_USERNAME}'>{CHANNEL_USERNAME}</a>\n"
            f"• Group: <a href='https://t.me/{GROUP_USERNAME}'>{GROUP_USERNAME}</a>\n\n"
            f"⚠️ After joining, click <b>VERIFY</b> button."
        )
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME}"),
            InlineKeyboardButton("💬 Join Group", url=f"https://t.me/{GROUP_USERNAME}")
        )
        keyboard.add(InlineKeyboardButton("✅ VERIFY MEMBERSHIP ✅", callback_data="verify_membership", style="success"))
        bot.send_message(message.chat.id, text, reply_markup=keyboard, parse_mode="HTML", disable_web_page_preview=True)
        return
    
    balance = get_user_balance(user_id)
    is_admin = (user_id == ADMIN_ID)
    text = main_menu_text(user_id, first_name, balance, "ACTIVE")
    bot.send_message(message.chat.id, text, reply_markup=main_menu_keyboard(is_admin), parse_mode="HTML")

@bot.message_handler(commands=['buy'])
def buy_cmd(message):
    user_id = message.from_user.id
    if not check_membership(user_id):
        bot.reply_to(message, "❌ Please join channel and group first!")
        return
    user_buy_state[user_id] = "waiting_amount"
    text = (
        "💰 <b>Buy Coins</b>\n\n"
        "Enter the amount in INR (minimum ₹1, maximum ₹10000).\n"
        "You will receive the same number of coins.\n\n"
        "Example: <code>50</code>"
    )
    bot.reply_to(message, text, parse_mode="HTML")

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
        bot.answer_callback_query(call.id, "❌ Please join both channel and group first!", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith("module_"))
def handle_module_callback(call):
    module = call.data.split("_")[1]
    user_id = call.from_user.id
    balance = get_user_balance(user_id)

    if module not in ["referral", "admin", "buy", "music"]:
        if not check_membership(user_id):
            bot.answer_callback_query(call.id, "❌ Please join channel and group first!", show_alert=True)
            return

    if module == "shopsy":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        text = shopsy_menu_text(user_id, balance, "ACTIVE")
        bot.send_message(call.message.chat.id, text, reply_markup=shopsy_menu_keyboard(), parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif module == "firebase":
        user_firebase_state[user_id] = False
        bot.delete_message(call.message.chat.id, call.message.message_id)
        text = firebase_menu_text(user_id, balance, "ACTIVE")
        bot.send_message(call.message.chat.id, text, reply_markup=firebase_menu_keyboard(), parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif module == "temp":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        text = temp_menu_text(user_id)
        bot.send_message(call.message.chat.id, text, reply_markup=temp_menu_keyboard(), parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif module == "flipkart":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        text = flipkart_menu_text(user_id, balance, "ACTIVE")
        bot.send_message(call.message.chat.id, text, reply_markup=flipkart_menu_keyboard(), parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif module == "instagram":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        text = instagram_menu_text(user_id, balance, "ACTIVE")
        bot.send_message(call.message.chat.id, text, reply_markup=instagram_menu_keyboard(), parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif module == "referral":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        referral_count = get_referral_count(user_id)
        text = referral_menu_text(user_id, balance, referral_count)
        bot.send_message(call.message.chat.id, text, reply_markup=referral_menu_keyboard(), parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif module == "buy":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        user_buy_state[user_id] = "waiting_amount"
        text = (
            "💰 <b>Buy Coins</b>\n\n"
            "Enter the amount in INR (minimum ₹1, maximum ₹10000).\n"
            "You will receive the same number of coins.\n\n"
            "Example: <code>50</code>"
        )
        bot.send_message(call.message.chat.id, text, parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif module == "music":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        user_music_state[user_id] = "waiting_for_search"
        text = (
            "🎵 <b>MUSIC DOWNLOADER</b>\n\n"
            "Send me a song name or artist name.\n"
            "I'll search and provide high-quality audio (320kbps).\n\n"
            "💡 Cost: <b>1 Credit</b> per song\n"
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

    # ---------- NEW: Session Extractor module ----------
    elif module == "session":
        balance = get_user_balance(user_id)
        if balance < 1:
            bot.answer_callback_query(call.id, "❌ Insufficient credits! Need 1 credit.", show_alert=True)
            return
        bot.delete_message(call.message.chat.id, call.message.message_id)
        user_session_state[user_id] = "waiting_phone"
        bot.send_message(
            call.message.chat.id,
            "🔐 <b>Flipkart/Shopsy Session Extractor</b>\n\n"
            "Enter your 10‑digit mobile number.\n"
            "I will request an OTP and extract your full session JSON.\n"
            "💰 Cost: <b>1 Credit</b> (only on success).\n\n"
            "Send <code>/cancel</code> to abort.",
            parse_mode="HTML"
        )
        bot.answer_callback_query(call.id)

# ==================== Referral callbacks ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith("referral_"))
def handle_referral_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    msg_id = call.message.message_id

    if call.data == "referral_get_link":
        if not check_membership(user_id):
            bot.answer_callback_query(call.id, "❌ Please join channel and group first!", show_alert=True)
            return
        link = get_referral_link(user_id)
        bot.answer_callback_query(call.id, "🔗 Link copied! Share it with friends.")
        bot.edit_message_text(
            f"🔗 <b>Your Referral Link</b>\n\n<code>{link}</code>\n\n"
            f"📤 Share this link with your friends!\n"
            f"🎁 You get <b>+{REFERRAL_BONUS} Credits</b> per referral (after 24h).\n"
            f"🎁 Your friend gets <b>+{NEW_USER_BONUS} Credits</b> on joining.\n\n"
            f"⚠️ Make sure your friend joins both channel and group!",
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

    if action == "send":
        user_firebase_state[user_id] = True
        bot.answer_callback_query(call.id, "📤 Ready! Send your APK file.")
        bot.edit_message_text(
            "📤 <b>Send APK</b>\n\n"
            "Please upload your APK file.\n"
            "I will analyze it for Firebase credentials and other sensitive data.\n\n"
            "⏱️ Analysis may take 30-60 seconds.\n"
            "💰 Cost: 2 Credits.\n"
            "Click <b>Remove APK</b> to cancel.",
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

    balance = get_user_balance(user_id)
    if balance < 2:
        bot.reply_to(message, f"❌ Insufficient credits! You need 2 credits. Your balance: {balance}")
        return

    update_user_balance(user_id, -2)
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
        update_user_balance(user_id, 2)
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

# ==================== Shopsy callbacks ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith("shopsy_"))
def handle_shopsy_callback(call):
    action = call.data.split("_")[1]
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    msg_id = call.message.message_id
    balance, status = get_user_balance(user_id), "ACTIVE"

    if action == "start":
        if get_user_balance(user_id) < 1:
            bot.answer_callback_query(call.id, "❌ Insufficient credits! Need 1 credit.", show_alert=True)
            return
        if user_id in shopsy_temp_data and shopsy_temp_data[user_id].get('mining_thread') and shopsy_temp_data[user_id]['mining_thread'].is_alive():
            bot.answer_callback_query(call.id, "⏳ Mining already in progress!", show_alert=True)
            return
        user_shopsy_state[user_id] = "waiting_phone"
        bot.delete_message(chat_id, msg_id)
        bot.send_message(chat_id, "📱 Please enter your Shopsy registered phone number (10 digits):")
        bot.answer_callback_query(call.id)

    elif action == "accounts":
        shopsy_bal = get_shopsy_balance(user_id)
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            f"📁 <b>My Shopsy Accounts</b>\n\n"
            f"💰 Shopsy Balance: <b>{shopsy_bal} SC</b>\n\n"
            f"💡 You can mine Shopsy coins using your registered phone.\n"
            f"Each mining run costs 1 Credit and gives 30-50 SC on average.",
            chat_id=chat_id, message_id=msg_id,
            reply_markup=shopsy_menu_keyboard(),
            parse_mode="HTML"
        )

    elif action == "howto":
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            "❓ <b>How To Use Shopsy Auto-Mine</b>\n\n"
            "1️⃣ Click <b>Start New Task</b> – bot will ask for your Shopsy phone number.\n"
            "2️⃣ Enter your 10-digit mobile number.\n"
            "3️⃣ If session exists, mining starts directly.\n"
            "4️⃣ If not, OTP sent – enter OTP to login.\n"
            "5️⃣ Bot will automatically play games and mine coins.\n"
            "6️⃣ Each run costs <b>1 Credit</b>.\n"
            "7️⃣ Earned Shopsy coins (SC) are added to your account.\n\n"
            "⚠️ Make sure you have sufficient balance before starting.",
            chat_id=chat_id, message_id=msg_id,
            reply_markup=shopsy_menu_keyboard(),
            parse_mode="HTML"
        )

# ---------- Shopsy Phone & OTP Handlers ----------
@bot.message_handler(func=lambda message: user_shopsy_state.get(message.from_user.id) == "waiting_phone")
def handle_shopsy_phone(message):
    user_id = message.from_user.id
    phone = message.text.strip()
    if not phone.isdigit() or len(phone) != 10:
        bot.reply_to(message, "❌ Invalid phone number. Please enter 10 digits.")
        return
    existing = shopsy.load_session(phone)
    if existing and existing.get("isLoggedIn"):
        user_shopsy_state[user_id] = None
        shopsy_temp_data[user_id] = {'phone': phone, 'session_data': existing}
        bot.reply_to(message, "✅ Session found! Starting mining...")
        start_shopsy_mining(user_id, message.chat.id)
        return
    user_shopsy_state[user_id] = "waiting_otp"
    shopsy_temp_data[user_id] = {'phone': phone, 'session_data': None}
    def request_otp_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        session_data, req_id = loop.run_until_complete(shopsy.request_otp(phone))
        if session_data and req_id:
            shopsy_temp_data[user_id]['session_data'] = session_data
            shopsy_temp_data[user_id]['req_id'] = req_id
            bot.send_message(user_id, "📲 OTP sent to your phone. Please enter the OTP:")
        else:
            bot.send_message(user_id, "❌ Failed to send OTP. Please try again later.")
            user_shopsy_state[user_id] = None
    threading.Thread(target=request_otp_thread).start()
    bot.reply_to(message, "⏳ Requesting OTP...")

@bot.message_handler(func=lambda message: user_shopsy_state.get(message.from_user.id) == "waiting_otp")
def handle_shopsy_otp(message):
    user_id = message.from_user.id
    otp = message.text.strip()
    if not otp.isdigit():
        bot.reply_to(message, "❌ Invalid OTP. Please enter numeric code.")
        return
    data = shopsy_temp_data.get(user_id, {})
    session_data = data.get('session_data')
    if not session_data:
        bot.reply_to(message, "❌ Session expired. Please start again.")
        user_shopsy_state[user_id] = None
        return
    def verify_otp_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        verified = loop.run_until_complete(shopsy.verify_otp(session_data, otp))
        if verified:
            shopsy_temp_data[user_id]['session_data'] = verified
            bot.send_message(user_id, "✅ Login successful! Starting mining...")
            user_shopsy_state[user_id] = None
            start_shopsy_mining(user_id, message.chat.id)
        else:
            bot.send_message(user_id, "❌ Invalid OTP. Please try again.")
    threading.Thread(target=verify_otp_thread).start()
    bot.reply_to(message, "⏳ Verifying OTP...")

# ==================== Shopsy Mining Thread ====================
def start_shopsy_mining(user_id, chat_id):
    data = shopsy_temp_data.get(user_id, {})
    session_data = data.get('session_data')
    phone = data.get('phone')
    if not session_data or not phone:
        bot.send_message(chat_id, "❌ Mining data missing. Please start again.")
        return

    msg = bot.send_message(chat_id, "⏳ Mining started...\n\nInitializing...")
    progress_messages = []

    def progress_callback(progress_text):
        nonlocal msg
        progress_messages.append(progress_text)
        if len(progress_messages) > 5:
            progress_messages.pop(0)
        display = "\n".join(progress_messages)
        try:
            bot.edit_message_text(f"⏳ Mining in progress...\n\n{display}", chat_id, msg.message_id)
        except:
            pass

    def mining_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(shopsy.mine_account_parallel(session_data, progress_callback, parallel_count=500))
        except Exception as e:
            result = {"status": "fail", "earned": 0, "msg": f"⚠️ Unexpected error: {str(e)[:100]}"}
        finally:
            loop.close()

        if result and result.get('status') == 'success':
            earned = result.get('earned', 0)
            final_coins = result.get('final_coins', 0)
            played = result.get('played', 0)
            total = result.get('total', 0)

            update_user_balance(user_id, -1)
            update_shopsy_balance(user_id, earned)
            final_text = (
                f"✅ <b>Mining Complete!</b>\n\n"
                f"🎯 Earned: <b>{earned} SC</b>\n"
                f"💰 Total Shopsy Coins: <b>{final_coins} SC</b>\n"
                f"🎮 Games Played: {played}/{total}\n"
                f"📱 Phone: +91{phone}\n\n"
                f"💎 Your Shopsy Balance: {get_shopsy_balance(user_id)} SC"
            )
            bot.edit_message_text(final_text, chat_id, msg.message_id, parse_mode="HTML")
        else:
            err = result.get('msg', 'Unknown error') if result else 'Failed to mine.'
            bot.edit_message_text(f"❌ Mining failed!\n\n{err}", chat_id, msg.message_id)

        shopsy_temp_data.pop(user_id, None)
        user_shopsy_state.pop(user_id, None)

    thread = threading.Thread(target=mining_thread)
    thread.daemon = True
    shopsy_temp_data[user_id]['mining_thread'] = thread
    thread.start()

# ---------- NEW: Session Extractor Phone & OTP Handlers ----------
@bot.message_handler(func=lambda message: user_session_state.get(message.from_user.id) == "waiting_phone")
def handle_session_phone(message):
    user_id = message.from_user.id
    phone = message.text.strip()
    if not phone.isdigit() or len(phone) != 10:
        bot.reply_to(message, "❌ Please enter a valid 10‑digit number (only digits).")
        return

    processing_msg = bot.reply_to(message, f"⏳ Requesting OTP for +91{phone}...")

    def request_otp_thread():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            session_data, req_id = loop.run_until_complete(shopsy.request_otp(phone))
            if session_data and req_id:
                session_temp_data[user_id] = {
                    'phone': phone,
                    'session_data': session_data,
                    'req_id': req_id
                }
                user_session_state[user_id] = "waiting_otp"
                bot.edit_message_text(
                    f"✅ OTP sent to +91{phone}.\n\nPlease enter the OTP you received.",
                    chat_id=message.chat.id,
                    message_id=processing_msg.message_id
                )
            else:
                bot.edit_message_text(
                    "❌ Failed to send OTP. Please try again later.",
                    chat_id=message.chat.id,
                    message_id=processing_msg.message_id
                )
                user_session_state[user_id] = None
                session_temp_data.pop(user_id, None)
        except Exception as e:
            logger.error(f"OTP request error: {e}")
            bot.edit_message_text(
                f"❌ Error requesting OTP: {str(e)[:100]}",
                chat_id=message.chat.id,
                message_id=processing_msg.message_id
            )
            user_session_state[user_id] = None
            session_temp_data.pop(user_id, None)

    threading.Thread(target=request_otp_thread, daemon=True).start()

@bot.message_handler(func=lambda message: user_session_state.get(message.from_user.id) == "waiting_otp")
def handle_session_otp(message):
    user_id = message.from_user.id
    otp = message.text.strip()
    if not otp.isdigit():
        bot.reply_to(message, "❌ Please enter a numeric OTP.")
        return

    data = session_temp_data.get(user_id, {})
    session_data = data.get('session_data')
    phone = data.get('phone')
    if not session_data or not phone:
        bot.reply_to(message, "❌ Session expired. Please start again.")
        user_session_state[user_id] = None
        return

    processing_msg = bot.reply_to(message, "⏳ Verifying OTP...")

    def verify_otp_thread():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            verified_session = loop.run_until_complete(shopsy.verify_otp(session_data, otp))
            if verified_session:
                balance = get_user_balance(user_id)
                if balance < 1:
                    bot.edit_message_text(
                        "❌ Insufficient credits! You need 1 Credit for this extraction.",
                        chat_id=message.chat.id,
                        message_id=processing_msg.message_id
                    )
                    user_session_state[user_id] = None
                    session_temp_data.pop(user_id, None)
                    return

                update_user_balance(user_id, -1)
                json_str = json.dumps(verified_session, indent=2, ensure_ascii=False)
                file_path = f"/tmp/{phone}_session.json"
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(json_str)

                with open(file_path, "rb") as f:
                    bot.send_document(
                        message.chat.id,
                        document=f,
                        file_name=f"{phone}_session.json",   # <-- FIXED
                        caption=f"✅ Session JSON for +91{phone} extracted successfully!\n💳 Cost: 1 Credit"
                    )
                os.remove(file_path)

                bot.delete_message(message.chat.id, processing_msg.message_id)
                log_usage(user_id, "Session Extractor", f"Phone: +91{phone}")
            else:
                bot.edit_message_text(
                    "❌ Invalid OTP or verification failed. Please try again.",
                    chat_id=message.chat.id,
                    message_id=processing_msg.message_id
                )
        except Exception as e:
            logger.error(f"OTP verification error: {e}")
            bot.edit_message_text(
                f"❌ Error during verification: {str(e)[:100]}",
                chat_id=message.chat.id,
                message_id=processing_msg.message_id
            )
        finally:
            user_session_state[user_id] = None
            session_temp_data.pop(user_id, None)

    threading.Thread(target=verify_otp_thread, daemon=True).start()

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

# ==================== Buy handler ====================
@bot.message_handler(func=lambda message: user_buy_state.get(message.from_user.id) == "waiting_amount")
def handle_buy_amount(message):
    user_id = message.from_user.id
    logger.info(f"Buy amount handler triggered for user {user_id} with text: {message.text}")
    try:
        amount = int(message.text.strip())
        if amount < 1 or amount > 10000:
            bot.reply_to(message, "❌ Amount must be between ₹1 and ₹10,000.")
            return
    except ValueError:
        bot.reply_to(message, "❌ Please send a valid number.")
        return
    order_id = f"ORD{int(time.time())}{random.randint(1000,9999)}"
    pending_purchases[user_id] = {'order_id': order_id, 'amount': amount}
    upi = f"upi://pay?pa=paytm.s1dw5n0@pty&pn=VC Payment Gateway&tid={order_id}&tr={order_id}&tn=VC Payment&am={amount}&cu=INR"
    qr_url = f"https://quickchart.io/qr?text={requests.utils.quote(upi)}"
    caption = (
        f"╔════════════════════╗\n"
        f"     💳 *VC PAYMENT GATEWAY*\n"
        f"╚════════════════════╝\n\n"
        f"💰 *Amount:* ₹{amount}\n"
        f"🆔 *Order ID:* {order_id}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"⚠️ Complete the payment using the QR code above.\n"
        f"After successful payment, tap the button below.\n"
        f"━━━━━━━━━━━━━━━━━━"
    )
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("✅ Check Payment", callback_data="buy_check"))
    bot.send_photo(message.chat.id, qr_url, caption=caption, reply_markup=keyboard, parse_mode="Markdown")
    user_buy_state[user_id] = None
    logger.info(f"QR sent for order {order_id} to user {user_id}")

# ==================== Flipkart checker callback ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith("flipkart_"))
def handle_flipkart_callback(call):
    bot.answer_callback_query(call.id, "📱 Send a 10-digit number to check.")

# ---------- FIXED: Flipkart phone handler now ignores active states ----------
@bot.message_handler(func=lambda message: message.text and message.text.isdigit() and len(message.text) == 10)
def handle_phone_number(message):
    user_id = message.from_user.id

    # Skip if user is in any active state (Shopsy, Buy, Firebase, Music, Session)
    if (user_shopsy_state.get(user_id) or 
        user_buy_state.get(user_id) or 
        user_firebase_state.get(user_id) or 
        user_music_state.get(user_id) or
        user_session_state.get(user_id)):   # <-- added session state
        return

    balance = get_user_balance(user_id)
    if balance < 1:
        bot.reply_to(message, "❌ Insufficient credits! You need 1 credit to check a number.")
        return
    update_user_balance(user_id, -1)
    processing = bot.reply_to(message, f"🔍 Checking <code>{message.text}</code> on Flipkart...", parse_mode="HTML")
    def check_thread():
        result = check_flipkart(message.text)
        new_balance = get_user_balance(user_id)
        bot.edit_message_text(
            f"📱 <b>Result for {message.text}</b>\n\n{result}\n\n💰 Remaining Credits: {new_balance}",
            chat_id=message.chat.id,
            message_id=processing.message_id,
            parse_mode="HTML"
        )
        log_usage(user_id, "Flipkart Checker", f"Number: {message.text}")
    threading.Thread(target=check_thread).start()

# ==================== Instagram callbacks ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith("instagram_"))
def handle_instagram_callback(call):
    action = call.data.split("_")[1]
    user_id = call.from_user.id

    if action == "single":
        user_instagram_state[user_id] = "single"
        bot.answer_callback_query(call.id, "📹 Send a single Instagram video URL.")
        bot.edit_message_text(
            "📹 <b>Single Download</b>\n\n"
            "Send me the Instagram video link.\n"
            "Example: <code>https://www.instagram.com/reel/xyz123/</code>\n\n"
            "💡 Costs 1 Credit.\n\n"
            "<i>Powered By Viediet Utility</i>",
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
            "💡 Costs 1 Credit per video.\n\n"
            "<i>Powered By Viediet Utility</i>",
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

    if not state:
        bot.reply_to(message, "📥 Please use the Instagram Downloader module from the main menu to send links.")
        return

    lines = message.text.strip().splitlines()
    urls = [line.strip() for line in lines if 'instagram.com' in line]

    if not urls:
        bot.reply_to(message, "❌ No valid Instagram URLs found.")
        return

    if state == "single":
        if balance < 1:
            bot.reply_to(message, "❌ Insufficient credits! You need 1 credit to download.")
            return
        update_user_balance(user_id, -1)
        processing = bot.reply_to(message, "⏳ Downloading reel...")
        def download_single():
            file_path = download_reel(urls[0])
            if file_path:
                try:
                    with open(file_path, "rb") as vid:
                        bot.send_video(message.chat.id, vid, caption="✅ Downloaded successfully!")
                    os.remove(file_path)
                    shutil.rmtree(os.path.dirname(file_path), ignore_errors=True)
                except Exception as e:
                    bot.send_message(message.chat.id, f"❌ Upload failed: {e}")
            else:
                bot.send_message(message.chat.id, "❌ Failed to download reel. Check URL or try again.")
            bot.delete_message(message.chat.id, processing.message_id)
        threading.Thread(target=download_single).start()

    elif state == "bulk":
        total_cost = len(urls)
        if balance < total_cost:
            bot.reply_to(message, f"❌ Insufficient credits! Need {total_cost} credits for {len(urls)} videos.")
            return
        update_user_balance(user_id, -total_cost)
        processing = bot.reply_to(message, f"⏳ Downloading {len(urls)} reels...")
        def download_bulk_thread():
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
            bot.delete_message(message.chat.id, processing.message_id)
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
        current_cost = get_config("firebase_cost", "2")
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            f"⚙️ <b>Set Costs</b>\n\nCurrent Firebase cost: <code>{current_cost}</code> credits\n\nTo change, send:\n`/setcost firebase 5`\n\n(Other modules can be added later)",
            chat_id=chat_id, message_id=msg_id,
            reply_markup=admin_panel_keyboard(), parse_mode="HTML"
        )

# ==================== Buy check callback ====================
@bot.callback_query_handler(func=lambda call: call.data == "buy_check")
def handle_buy_check(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    msg_id = call.message.message_id
    if user_id not in pending_purchases:
        bot.answer_callback_query(call.id, "❌ No pending purchase found.")
        return
    purchase = pending_purchases[user_id]
    order_id = purchase['order_id']
    amount = purchase['amount']
    API_KEY = os.environ.get("VC_API_KEY")
    if not API_KEY:
        bot.answer_callback_query(call.id, "❌ Payment gateway not configured.")
        return
    url = f"https://vcapi.vcstore.site/payment_api.php?api_key={API_KEY}&order_id={order_id}&amount={amount}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success' or data.get('success') == True:
                coins = amount
                update_user_balance(user_id, coins)
                del pending_purchases[user_id]
                bot.edit_message_text(
                    f"✅ <b>Payment Verified!</b>\n\n"
                    f"💰 Added {coins} coins to your account.\n"
                    f"💳 Order ID: {order_id}\n"
                    f"📊 New Balance: {get_user_balance(user_id)}",
                    chat_id=chat_id, message_id=msg_id,
                    parse_mode="HTML"
                )
                bot.answer_callback_query(call.id, "✅ Payment successful!")
                log_usage(user_id, "Buy Coins", f"Amount: {amount}, Order: {order_id}")
            else:
                bot.edit_message_text(
                    "❌ <b>Payment Not Verified</b>\n\n"
                    "We could not confirm your payment. Please check your UPI transaction or try again later.",
                    chat_id=chat_id, message_id=msg_id,
                    parse_mode="HTML"
                )
                bot.answer_callback_query(call.id, "❌ Payment not found.")
        else:
            bot.answer_callback_query(call.id, f"❌ API error: {response.status_code}")
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ Error: {str(e)[:50]}")

# ---------- Music Handlers ----------
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
    
    bot.edit_message_text(f"🎵 <b>Search Results for</b>: {query}\n\nSelect a song to download (1 Credit):",
                          chat_id=message.chat.id, message_id=searching_msg.message_id,
                          reply_markup=keyboard, parse_mode="HTML")
    
    log_usage(user_id, "Music Search", query)
    user_music_state[user_id] = None

@bot.callback_query_handler(func=lambda call: call.data.startswith("music_song_"))
def handle_music_song_callback(call):
    user_id = call.from_user.id
    song_id = call.data.replace("music_song_", "")
    bot.answer_callback_query(call.id, "🔄 Fetching song...")
    
    balance = get_user_balance(user_id)
    if balance < 1:
        bot.edit_message_text("❌ Insufficient credits! You need 1 credit to download a song.",
                              chat_id=call.message.chat.id, message_id=call.message.message_id)
        return
    
    update_user_balance(user_id, -1)
    processing_msg = bot.send_message(call.message.chat.id, "⏳ Downloading high-quality audio...")
    
    try:
        song_details = get_song_details(song_id)
        if not song_details or not song_details.get("url"):
            update_user_balance(user_id, 1)
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
            update_user_balance(user_id, 1)
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
        update_user_balance(user_id, 1)
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

# ---------- Admin command to manually check referrals ----------
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
    logger.info("🤖 Bot is starting with Shopsy mining integrated...")
    try:
        bot.remove_webhook()
        time.sleep(5)
    except:
        pass
    while True:
        try:
            bot.polling(non_stop=True, interval=0, timeout=60)
        except Exception as e:
            logger.error(f"Polling error: {e}")
            time.sleep(5)
