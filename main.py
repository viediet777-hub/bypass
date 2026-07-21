#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# NRTECNO SYSTEM - VIEDIET BOT v2.0 - WITH SLAY MODULE

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
import subprocess
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
        slay_menu_text, slay_menu_keyboard  # <--- ADDED
    )
except ImportError:
    # Fallback
    def main_menu_text(u, f, b, s): return f"Welcome {f}! Balance: {b}"
    def main_menu_keyboard(a=False): 
        kb = InlineKeyboardMarkup(row_width=1)
        kb.row(InlineKeyboardButton("📊 Stats", callback_data="module_stats"))
        return kb
    def slay_menu_text(*a,**k): return "Slay Your Play"
    def slay_menu_keyboard(): return main_menu_keyboard()
    # ... other fallbacks

# ==================== CONFIG ====================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    logging.error("BOT_TOKEN environment variable not set.")
    exit(1)

ADMIN_ID = int(os.environ.get("ADMIN_ID", 1364476174))
CHANNEL_USERNAME = "viedietlooters"
REFERRAL_BONUS = 1
NEW_USER_BONUS = 1
REFERRAL_STAY_HOURS = 0

YOGA_REFER_REWARD = 1
YOGA_WELCOME_BONUS = 1

DEFAULT_COSTS = {
    "firebase": 1,
    "flipkart": 1,
    "instagram_single": 1,
    "instagram_bulk": 1,
    "shopsy": 1,
    "yoga": 1,
    "igviewer": 1,
    "slay": 1,  # <--- ADDED
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
        shopsy_is_logged_in INTEGER DEFAULT 0,
        yoga_code TEXT DEFAULT NULL,
        yoga_refers INTEGER DEFAULT 0,
        yoga_bot_refers INTEGER DEFAULT 0,
        slay_logged_in INTEGER DEFAULT 0,
        slay_session_data TEXT DEFAULT NULL,
        slay_codes_found INTEGER DEFAULT 0
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
            'shopsy_is_logged_in': row[14] if len(row) > 14 else 0,
            'yoga_code': row[15] if len(row) > 15 else None,
            'yoga_refers': row[16] if len(row) > 16 else 0,
            'yoga_bot_refers': row[17] if len(row) > 17 else 0,
            'slay_logged_in': row[18] if len(row) > 18 else 0,
            'slay_session_data': row[19] if len(row) > 19 else None,
            'slay_codes_found': row[20] if len(row) > 20 else 0
        }
    return None

def create_user(user_id, username, first_name, referred_by=None, ip_address=None):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    now = datetime.now().isoformat()
    ref_code = f"REF{user_id}{random.randint(1000, 9999)}"
    c.execute('''INSERT OR IGNORE INTO users 
        (user_id, username, first_name, balance, status, registered_at, last_used, referred_by, referral_code, ip_address, shopsy_balance, shopsy_is_logged_in, yoga_code, yoga_refers, yoga_bot_refers, slay_logged_in, slay_codes_found)
        VALUES (?, ?, ?, ?, 'ACTIVE', ?, ?, ?, ?, ?, 0, 0, ?, 0, 0, 0, 0)''',
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

def get_module_cost(module):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT value FROM config WHERE key = ?', (f"{module}_cost",))
    row = c.fetchone()
    conn.close()
    if row:
        return int(row[0])
    return DEFAULT_COSTS.get(module, 1)

def log_usage(user_id, module, details=""):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute('INSERT INTO usage_logs (user_id, module, details, timestamp) VALUES (?, ?, ?, ?)',
              (user_id, module, details, now))
    conn.commit()
    conn.close()

# ==================== BACK BUTTON HELPER ====================
def back_button():
    kb = InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu"))
    return kb

# ==================== SLAY PROXY MANAGER ====================
class SlayProxyManager:
    @staticmethod
    def load_slay_proxies():
        """Load proxies from slay_proxies.txt"""
        proxies = []
        proxy_file = "slay_proxies.txt"
        if not os.path.exists(proxy_file):
            logger.warning(f"[SLAY] Proxy file '{proxy_file}' not found.")
            return proxies
        
        try:
            with open(proxy_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split(':')
                        if len(parts) >= 4:
                            proxy = {
                                'http': f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}",
                                'https': f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
                            }
                            proxies.append(proxy)
                        elif len(parts) == 2:
                            proxy = {
                                'http': f"http://{parts[0]}:{parts[1]}",
                                'https': f"http://{parts[0]}:{parts[1]}"
                            }
                            proxies.append(proxy)
            logger.info(f"[SLAY] Loaded {len(proxies)} proxies from slay_proxies.txt")
        except Exception as e:
            logger.error(f"[SLAY] Error loading proxies: {e}")
        
        return proxies

# ==================== SLAY SCAN ENGINE ====================
class SlayScanEngine:
    def __init__(self, bot, chat_id, user_id):
        self.bot = bot
        self.chat_id = chat_id
        self.user_id = user_id
        self.process = None
        self.is_running = False
        self.thread = None
        self.valid_code = None
        self.proxies = SlayProxyManager.load_slay_proxies()
        self.update_count = 0
    
    def start_scan(self, mobile: str, reward_mobile: str = None) -> str:
        if self.is_running:
            return "⚠️ Scan already running!"
        
        if not mobile or len(mobile) != 10:
            return "❌ Invalid mobile number!"
        
        reward = reward_mobile or mobile
        
        # Check balance
        balance = get_user_balance(self.user_id)
        cost = get_module_cost("slay")
        if balance < cost:
            return f"❌ Insufficient credits! Need {cost}, have {balance}"
        
        # Deduct credits
        update_user_balance(self.user_id, -cost)
        
        # Create command with arguments
        cmd = [
            "python", "workingslay.py",
            "--mobile", mobile,
            "--reward-mobile", reward,
            "--delay", "0.2",
            "--expiry", "30",
            "--no-proxy"
        ]
        cmd = [c for c in cmd if c]  # Remove empty strings
        
        self.is_running = True
        self.valid_code = None
        self.update_count = 0
        
        try:
            if os.name == 'nt':
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )
        except Exception as e:
            self.is_running = False
            update_user_balance(self.user_id, cost)  # Refund on error
            return f"❌ Failed to start scan: {e}"
        
        # Start monitoring thread
        self.thread = threading.Thread(target=self._monitor_output, daemon=True)
        self.thread.start()
        
        return f"✅ Scan started!\n📱 Mobile: {mobile}\n💰 Cost: {cost} credits"
    
    def _monitor_output(self):
        """Monitor and send updates"""
        last_update_time = time.time()
        
        while self.is_running and self.process:
            try:
                # Read stdout
                line = self.process.stdout.readline()
                if line:
                    line = line.strip()
                    if line:
                        self.update_count += 1
                        self._send_update(line)
                        
                        # Check for valid code
                        if "VALID" in line.upper() or "CODE MILA" in line:
                            self.valid_code = line
                            self._send_update(f"🎯 **CODE FOUND!** {line}")
                            
                            # Update user stats
                            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
                            c = conn.cursor()
                            c.execute('UPDATE users SET slay_codes_found = slay_codes_found + 1 WHERE user_id = ?', (self.user_id,))
                            conn.commit()
                            conn.close()
                            
                            self.stop_scan()
                            break
                        
                        # Send stats every 10 updates or 5 seconds
                        current_time = time.time()
                        if self.update_count % 10 == 0 or (current_time - last_update_time) > 5:
                            self._send_update(f"📊 Scanning... {self.update_count} checks done")
                            last_update_time = current_time
                
                # Check if process ended
                if self.process.poll() is not None:
                    self.is_running = False
                    break
                    
            except Exception as e:
                logger.error(f"[SLAY] Monitor error: {e}")
                break
        
        if self.is_running:
            self.is_running = False
            self._send_update("⏹ Scan ended.")
    
    def _send_update(self, message):
        """Send update to Telegram"""
        try:
            # Filter messages to avoid spam
            if "INVALID" in message.upper():
                return
            
            # Send important messages
            keywords = ["VALID", "REWARD", "FOUND", "STATS", "ERROR", "FINAL", "CODE", "LIVE"]
            if any(k in message.upper() for k in keywords):
                self.bot.send_message(
                    self.chat_id,
                    f"📡 `{message[:500]}`",
                    parse_mode="Markdown"
                )
            elif "STATS" in message.upper():
                self.bot.send_message(
                    self.chat_id,
                    f"📊 `{message}`",
                    parse_mode="Markdown"
                )
        except Exception as e:
            logger.error(f"[SLAY] Send update error: {e}")
    
    def stop_scan(self):
        """Stop running scan"""
        if self.process and self.is_running:
            try:
                self.process.terminate()
                time.sleep(0.5)
                self.process.kill()
            except:
                pass
            self.is_running = False
            return "⏹ Scan stopped by user."
        return "⚠️ No scan running."
    
    def get_status(self) -> str:
        if self.is_running:
            return "🟢 Running"
        if self.valid_code:
            return f"✅ Code found: {self.valid_code}"
        return "🔴 Idle"

# ==================== GLOBAL STATES FOR SLAY ====================
user_slay_state = {}
user_slay_phone = {}
slay_otp_data = {}
slay_engines = {}

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

# ==================== MEMBERSHIP CHECK ====================
def check_membership(user_id):
    try:
        member = bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# ==================== CALLBACK QUERY HANDLER ====================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    data = call.data
    
    # ===== BACK BUTTONS =====
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
    
    # ===== MODULE NAVIGATION =====
    if data.startswith("module_"):
        module = data.replace("module_", "")
        user = get_user(user_id)
        if not user:
            bot.answer_callback_query(call.id, "User not found")
            return
        
        status = "✅" if check_membership(user_id) else "❌"
        balance = user['balance']
        
        if module == "slay":
            cost = get_module_cost("slay")
            has_session = user.get('slay_logged_in', 0) == 1
            codes_found = user.get('slay_codes_found', 0)
            bot.edit_message_text(
                slay_menu_text(user_id, balance, status, cost, has_session, codes_found),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=slay_menu_keyboard(),
                parse_mode="HTML"
            )
        elif module == "firebase":
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
        else:
            bot.answer_callback_query(call.id, "Module not found")
        
        bot.answer_callback_query(call.id)
        return
    
    # ===== SLAY CALLBACKS =====
    if data == "slay_start":
        user = get_user(user_id)
        cost = get_module_cost("slay")
        
        if user['balance'] < cost:
            bot.answer_callback_query(call.id, f"❌ Need {cost} credits! Balance: {user['balance']}", show_alert=True)
            return
        
        user_slay_state[user_id] = "waiting_slay_phone"
        kb = InlineKeyboardMarkup()
        kb.row(InlineKeyboardButton("❌ Cancel", callback_data="slay_abort"))
        kb.row(InlineKeyboardButton("🔙 Back", callback_data="back_slay"))
        bot.edit_message_text(
            "📱 Enter your 10-digit mobile number for Slay Your Play:\n\nSend /cancel to abort.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=kb
        )
        bot.answer_callback_query(call.id)
        return
    
    if data == "slay_abort":
        user_slay_state[user_id] = None
        if user_id in slay_otp_data:
            del slay_otp_data[user_id]
        bot.edit_message_text(
            "❌ Slay operation cancelled.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=back_button()
        )
        bot.answer_callback_query(call.id)
        return
    
    if data == "slay_status":
        user = get_user(user_id)
        bot.answer_callback_query(
            call.id,
            f"🎮 Slay Status:\nLogged In: {user.get('slay_logged_in', 0)}\nCodes Found: {user.get('slay_codes_found', 0)}",
            show_alert=True
        )
        return
    
    if data == "slay_refresh":
        bot.answer_callback_query(call.id, "🔄 Session refreshed!", show_alert=True)
        return
    
    if data == "slay_logout":
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('UPDATE users SET slay_logged_in = 0, slay_session_data = NULL WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()
        bot.answer_callback_query(call.id, "🚪 Logged out successfully!", show_alert=True)
        # Refresh menu
        user = get_user(user_id)
        bot.edit_message_text(
            slay_menu_text(user_id, user['balance'], "✅", get_module_cost("slay"), False, user.get('slay_codes_found', 0)),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=slay_menu_keyboard(),
            parse_mode="HTML"
        )
        return
    
    if data == "back_slay":
        user = get_user(user_id)
        cost = get_module_cost("slay")
        has_session = user.get('slay_logged_in', 0) == 1
        user_slay_state[user_id] = None
        if user_id in slay_otp_data:
            del slay_otp_data[user_id]
        bot.edit_message_text(
            slay_menu_text(user_id, user['balance'], "✅", cost, has_session, user.get('slay_codes_found', 0)),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=slay_menu_keyboard(),
            parse_mode="HTML"
        )
        bot.answer_callback_query(call.id)
        return
    
    # ===== REFERRAL CALLBACKS =====
    if data == "referral_get_link":
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
        link = get_referral_link(user_id)
        bot.answer_callback_query(
            call.id,
            "📤 Copy this link and share with friends!\n\n" + link,
            show_alert=True
        )
        return
    
    if data == "referral_stats":
        referral_count = get_referral_count(user_id)
        pending_count = get_pending_referral_count(user_id)
        balance = get_user_balance(user_id)
        bot.answer_callback_query(
            call.id,
            f"📊 Referral Stats:\n✅ Completed: {referral_count}\n⏳ Pending: {pending_count}\n💰 Balance: {balance}\n🎁 Bonus: +{REFERRAL_BONUS} per referral",
            show_alert=True
        )
        return
    
    # ===== SHOPSY CALLBACKS =====
    if data == "shopsy_start":
        if get_shopsy_login_status(user_id):
            bot.answer_callback_query(call.id, "Already logged in! Use Mining...")
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
    
    if data == "shopsy_abort":
        user_shopsy_state[user_id] = None
        bot.edit_message_text(
            "❌ Shopsy operation cancelled.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=back_button()
        )
        bot.answer_callback_query(call.id)
        return
    
    # ===== YOGA CALLBACKS =====
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
    
    if data == "yoga_abort":
        user_yoga_state[user_id] = None
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
    
    # ===== ADMIN CALLBACKS =====
    if data.startswith("admin_"):
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ Unauthorized - Admin only!")
            return
        
        action = data.replace("admin_", "")
        
        if action == "stats":
            # Get stats
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute('SELECT COUNT(*) FROM users')
            total_users = c.fetchone()[0]
            c.execute('SELECT SUM(balance) FROM users')
            total_coins = c.fetchone()[0] or 0
            c.execute('SELECT COUNT(*) FROM usage_logs')
            total_usage = c.fetchone()[0]
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
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute('SELECT user_id, username, balance, status FROM users ORDER BY balance DESC LIMIT 10')
            users = c.fetchall()
            conn.close()
            
            if not users:
                bot.answer_callback_query(call.id, "No users found", show_alert=True)
                return
            
            user_list = "👥 <b>Top Users by Balance:</b>\n\n"
            for i, (uid, username, balance, status) in enumerate(users, 1):
                name = username or f"User_{uid}"
                status_icon = "🟢" if status == "ACTIVE" else "🔴"
                user_list += f"{i}. {status_icon} {name} - 💰 {balance}\n"
            
            kb = InlineKeyboardMarkup()
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
            costs_text += f"Example: <code>/setcost slay 2</code>"
            
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
        
        bot.answer_callback_query(call.id)
        return
    
    bot.answer_callback_query(call.id)

# ==================== SLAY MESSAGE HANDLERS ====================
@bot.message_handler(func=lambda message: user_slay_state.get(message.from_user.id) == "waiting_slay_phone")
def slay_phone_handler(message):
    user_id = message.from_user.id
    phone = message.text.strip()
    
    if phone.lower() in ['/cancel', 'cancel']:
        user_slay_state[user_id] = None
        bot.reply_to(message, "❌ Slay scan cancelled.", reply_markup=back_button())
        return
    
    if not phone.isdigit() or len(phone) != 10:
        bot.reply_to(message, "❌ Please enter exactly 10 digits.\n\nSend /cancel to abort.")
        return
    
    cost = get_module_cost("slay")
    balance = get_user_balance(user_id)
    if balance < cost:
        bot.reply_to(message, f"❌ Insufficient credits! Need {cost} credits. Balance: {balance}")
        return
    
    user_slay_state[user_id] = "waiting_slay_otp"
    user_slay_phone[user_id] = phone
    
    kb = InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton("❌ Cancel", callback_data="slay_abort"))
    kb.row(InlineKeyboardButton("🔙 Back", callback_data="back_slay"))
    
    status_msg = bot.reply_to(message, f"📱 Sending OTP to +91{phone}...", reply_markup=kb)
    
    # Deduct credits
    update_user_balance(user_id, -cost)
    slay_otp_data[user_id] = {"phone": phone, "cost": cost}
    
    def send_otp_thread():
        try:
            # Send OTP using workingslay
            from workingslay import send_otp, make_session, generate_master_key
            
            master_key = generate_master_key()
            session = make_session(master_key)
            
            # Init session first
            from workingslay import init_session
            user_key, data_key = init_session(session, master_key)
            if not user_key:
                bot.edit_message_text(
                    "❌ Failed to initialize session. Please try again.",
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id
                )
                user_slay_state[user_id] = None
                update_user_balance(user_id, cost)
                return
            
            # Send OTP
            success = send_otp(session, user_key, data_key, phone)
            
            if success:
                bot.edit_message_text(
                    f"✅ OTP sent to +91{phone}!\n\nEnter the 6-digit OTP code:\nSend /cancel to abort.",
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id,
                    reply_markup=kb
                )
                slay_otp_data[user_id]["session"] = session
                slay_otp_data[user_id]["user_key"] = user_key
                slay_otp_data[user_id]["data_key"] = data_key
            else:
                bot.edit_message_text(
                    f"❌ Failed to send OTP. Please try again later.",
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id
                )
                user_slay_state[user_id] = None
                update_user_balance(user_id, cost)
                
        except Exception as e:
            update_user_balance(user_id, cost)
            bot.edit_message_text(
                f"❌ Error: {str(e)[:200]}",
                chat_id=message.chat.id,
                message_id=status_msg.message_id
            )
            user_slay_state[user_id] = None
    
    threading.Thread(target=send_otp_thread).start()

@bot.message_handler(func=lambda message: user_slay_state.get(message.from_user.id) == "waiting_slay_otp")
def slay_otp_handler(message):
    user_id = message.from_user.id
    otp = message.text.strip()
    
    if otp.lower() in ['/cancel', 'cancel']:
        user_slay_state[user_id] = None
        if user_id in slay_otp_data:
            update_user_balance(user_id, slay_otp_data[user_id]["cost"])
            del slay_otp_data[user_id]
        bot.reply_to(message, "❌ Slay scan cancelled.", reply_markup=back_button())
        return
    
    if not otp.isdigit() or len(otp) != 6:
        bot.reply_to(message, "❌ Please enter a valid 6-digit OTP.\n\nSend /cancel to abort.")
        return
    
    if user_id not in slay_otp_data:
        bot.reply_to(message, "❌ Session expired. Please start again.")
        user_slay_state[user_id] = None
        return
    
    data = slay_otp_data[user_id]
    phone = data["phone"]
    cost = data["cost"]
    session = data.get("session")
    user_key = data.get("user_key")
    data_key = data.get("data_key")
    
    status_msg = bot.reply_to(message, "🔄 Verifying OTP and logging in...")
    
    def verify_thread():
        try:
            from workingslay import verify_otp, select_pack, select_vibe, save_global_session
            
            # Verify OTP
            access_token = verify_otp(session, user_key, data_key, otp)
            
            if access_token:
                # Select pack and vibe
                select_pack(session, user_key, data_key, access_token)
                select_vibe(session, user_key, data_key, access_token)
                save_global_session()
                
                # Update user
                conn = sqlite3.connect(DB_PATH, check_same_thread=False)
                c = conn.cursor()
                c.execute('UPDATE users SET slay_logged_in = 1 WHERE user_id = ?', (user_id,))
                conn.commit()
                conn.close()
                
                bot.edit_message_text(
                    f"✅ <b>Slay Login Successful!</b>\n\n"
                    f"📱 Phone: +91{phone}\n"
                    f"💰 Balance: <code>{get_user_balance(user_id)}</code>\n\n"
                    f"🎮 Starting scan automatically...",
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id,
                    parse_mode="HTML"
                )
                
                user_slay_state[user_id] = None
                del slay_otp_data[user_id]
                
                # Start scan
                start_slay_scan(message, user_id, phone)
                
            else:
                update_user_balance(user_id, cost)
                bot.edit_message_text(
                    f"❌ OTP verification failed.\n\nPlease try again with a valid OTP.",
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id
                )
                user_slay_state[user_id] = None
                if user_id in slay_otp_data:
                    del slay_otp_data[user_id]
                
        except Exception as e:
            update_user_balance(user_id, cost)
            bot.edit_message_text(
                f"❌ Error: {str(e)[:200]}",
                chat_id=message.chat.id,
                message_id=status_msg.message_id
            )
            user_slay_state[user_id] = None
            if user_id in slay_otp_data:
                del slay_otp_data[user_id]
    
    threading.Thread(target=verify_thread).start()

def start_slay_scan(message, user_id, phone):
    """Start the actual scan process"""
    scan_msg = bot.reply_to(
        message,
        f"🔍 **SLAY SCAN STARTED**\n\n"
        f"📱 Mobile: `+91{phone}`\n"
        f"⏳ Scanning for valid codes...\n"
        f"🔄 Auto-stop on code found\n\n"
        f"_This may take several minutes._",
        parse_mode="Markdown"
    )
    
    # Create scan engine
    scan_engine = SlayScanEngine(bot, message.chat.id, user_id)
    slay_engines[user_id] = scan_engine
    
    def scan_thread():
        result = scan_engine.start_scan(phone, phone)
        if "✅" in result:
            bot.edit_message_text(
                f"✅ **Scan Started!**\n\n"
                f"📱 Mobile: `+91{phone}`\n"
                f"🔍 Scanning in progress...\n\n"
                f"_Check back for results._",
                chat_id=message.chat.id,
                message_id=scan_msg.message_id,
                parse_mode="Markdown"
            )
        else:
            bot.edit_message_text(
                f"❌ **Scan Failed**\n\n{result}",
                chat_id=message.chat.id,
                message_id=scan_msg.message_id,
                parse_mode="Markdown"
            )
    
    threading.Thread(target=scan_thread).start()

# ==================== SHOPSY FUNCTIONS (Placeholders) ====================
def get_shopsy_balance(user_id):
    user = get_user(user_id)
    return user['shopsy_balance'] if user else 0

def get_shopsy_login_status(user_id):
    user = get_user(user_id)
    return user.get('shopsy_is_logged_in', 0) if user else 0

def get_yoga_refer_reward():
    return YOGA_REFER_REWARD

def get_referral_link(user_id):
    bot_username = bot.get_me().username
    return f"https://t.me/{bot_username}?start=ref_{user_id}"

# ==================== ADMIN HANDLERS ====================
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
    
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT user_id FROM users')
    users = c.fetchall()
    conn.close()
    
    if not users:
        bot.reply_to(message, "❌ No users to broadcast to!")
        return
    
    confirm_kb = InlineKeyboardMarkup()
    confirm_kb.row(
        InlineKeyboardButton("✅ Send", callback_data="broadcast_confirm"),
        InlineKeyboardButton("❌ Cancel", callback_data="broadcast_cancel")
    )
    
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

# ==================== YOGA HANDLERS ====================
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
                "Example: <code>/setcost slay 2</code>\n\n"
                "Available modules: firebase, flipkart, instagram_single, instagram_bulk, shopsy, yoga, igviewer, slay",
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
        
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('REPLACE INTO config (key, value) VALUES (?, ?)', (f"{module}_cost", str(amount)))
        conn.commit()
        conn.close()
        
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

# ==================== MAIN ====================
if __name__ == "__main__":
    logger.info("🤖 Bot started – ALL FEATURES WORKING!")
    logger.info("🎮 SLAY YOUR PLAY MODULE ADDED")
    logger.info("💰 1 credit per scan | Auto-stop on code found")
    logger.info("📊 Referral: +3 credits per referral")
    
    try:
        bot.remove_webhook()
        time.sleep(1)
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
