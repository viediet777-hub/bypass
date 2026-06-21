#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import sys
import time
import threading
import sqlite3
import random
import string
import re
import hashlib
import zipfile
import shutil
import tempfile
from datetime import datetime, timedelta

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import instaloader

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

# ==================== CONFIG ====================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    logging.error("BOT_TOKEN environment variable not set.")
    sys.exit(1)

ADMIN_ID = int(os.environ.get("ADMIN_ID", 1364476174))
CHANNEL_USERNAME = "viedietlooters"
GROUP_USERNAME = "viedietlooterschat"
REFERRAL_BONUS = 2
NEW_USER_BONUS = 5
MIN_ACCOUNT_AGE_DAYS = 7
REFERRAL_STAY_HOURS = 24

# ==================== LOGGING ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== DATABASE SETUP ====================
# Use an absolute path that is guaranteed writable (e.g., /tmp on Linux)
DB_DIR = os.path.dirname(os.path.abspath(__file__))
if not os.access(DB_DIR, os.W_OK):
    DB_DIR = tempfile.gettempdir()
DB_PATH = os.path.join(DB_DIR, "viediet_bot.db")
logger.info(f"Using database at: {DB_PATH}")

def get_db_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
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
            last_check TEXT DEFAULT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referrer_id INTEGER,
            referred_id INTEGER UNIQUE,
            join_timestamp TEXT,
            leave_timestamp TEXT DEFAULT NULL,
            points_awarded INTEGER DEFAULT 0,
            is_valid INTEGER DEFAULT 0
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS pending_referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referrer_id INTEGER,
            referred_id INTEGER UNIQUE,
            join_timestamp TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS usage_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            module TEXT,
            details TEXT,
            timestamp TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    conn.commit()
    conn.close()
    logger.info("Database initialized.")

init_db()

# ==================== BOT INIT ====================
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ==================== SAFE DATABASE HELPER ====================
def safe_db_query(query, params=(), fetch_one=False, fetch_all=False, commit=False):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute(query, params)
        if commit:
            conn.commit()
        result = None
        if fetch_one:
            result = c.fetchone()
        elif fetch_all:
            result = c.fetchall()
        conn.close()
        return result
    except Exception as e:
        logger.error(f"DB error: {e} | Query: {query[:100]}")
        return None

# ==================== DATABASE FUNCTIONS ====================
def get_user(user_id):
    row = safe_db_query('SELECT * FROM users WHERE user_id = ?', (user_id,), fetch_one=True)
    if row:
        return {
            'user_id': row[0], 'username': row[1], 'first_name': row[2],
            'balance': row[3], 'status': row[4], 'registered_at': row[5],
            'last_used': row[6], 'referred_by': row[7], 'referral_code': row[8],
            'account_age_days': row[9], 'is_valid': row[10], 'ip_address': row[11],
            'last_check': row[12]
        }
    return None

def create_user(user_id, username, first_name, referred_by=None, ip_address=None):
    now = datetime.now().isoformat()
    ref_code = f"REF{user_id}{random.randint(1000, 9999)}"
    safe_db_query(
        '''INSERT OR IGNORE INTO users 
           (user_id, username, first_name, balance, status, registered_at, last_used, referred_by, referral_code, ip_address)
           VALUES (?, ?, ?, ?, 'ACTIVE', ?, ?, ?, ?, ?)''',
        (user_id, username, first_name, NEW_USER_BONUS, now, now, referred_by, ref_code, ip_address),
        commit=True
    )
    if referred_by:
        add_pending_referral(referred_by, user_id)
    return NEW_USER_BONUS

def update_user_balance(user_id, delta):
    safe_db_query('UPDATE users SET balance = balance + ? WHERE user_id = ?', (delta, user_id), commit=True)

def get_user_balance(user_id):
    user = get_user(user_id)
    return user['balance'] if user else 15

def get_referral_count(user_id):
    row = safe_db_query('SELECT COUNT(*) FROM referrals WHERE referrer_id = ? AND is_valid = 1', (user_id,), fetch_one=True)
    return row[0] if row else 0

def get_pending_referral_count(user_id):
    row = safe_db_query('SELECT COUNT(*) FROM pending_referrals WHERE referrer_id = ?', (user_id,), fetch_one=True)
    return row[0] if row else 0

def add_pending_referral(referrer_id, referred_id):
    now = datetime.now().isoformat()
    safe_db_query(
        'INSERT OR IGNORE INTO pending_referrals (referrer_id, referred_id, join_timestamp) VALUES (?, ?, ?)',
        (referrer_id, referred_id, now),
        commit=True
    )

def log_usage(user_id, module, details=""):
    now = datetime.now().isoformat()
    safe_db_query(
        'INSERT INTO usage_logs (user_id, module, details, timestamp) VALUES (?, ?, ?, ?)',
        (user_id, module, details, now),
        commit=True
    )
    safe_db_query('UPDATE users SET last_used = ? WHERE user_id = ?', (now, user_id), commit=True)

def get_all_users():
    rows = safe_db_query('SELECT user_id, username, balance, status FROM users ORDER BY balance DESC', fetch_all=True)
    return rows if rows else []

def get_total_users():
    row = safe_db_query('SELECT COUNT(*) FROM users', fetch_one=True)
    return row[0] if row else 0

def get_total_coins():
    row = safe_db_query('SELECT SUM(balance) FROM users', fetch_one=True)
    return row[0] if row else 0

def get_total_usage():
    row = safe_db_query('SELECT COUNT(*) FROM usage_logs', fetch_one=True)
    return row[0] if row else 0

def get_config(key, default=None):
    row = safe_db_query('SELECT value FROM config WHERE key = ?', (key,), fetch_one=True)
    return row[0] if row else default

def set_config(key, value):
    safe_db_query('REPLACE INTO config (key, value) VALUES (?, ?)', (key, value), commit=True)

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

def get_referral_link(user_id):
    bot_username = bot.get_me().username
    return f"https://t.me/{bot_username}?start=ref_{user_id}"

def check_and_award_referrals():
    conn = get_db_connection()
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
                    c.execute('''
                        INSERT INTO referrals (referrer_id, referred_id, join_timestamp, points_awarded, is_valid)
                        VALUES (?, ?, ?, ?, 1)
                    ''', (referrer_id, referred_id, join_ts, REFERRAL_BONUS))
                    c.execute('DELETE FROM pending_referrals WHERE id = ?', (pid,))
                    conn.commit()
                    try:
                        bot.send_message(referrer_id, f"🎉 <b>Referral Bonus!</b>\n\nYou earned <b>+{REFERRAL_BONUS} Credits</b> for referring a user who stayed in our community for 24 hours!\n💰 New balance: {get_user_balance(referrer_id)}", parse_mode="HTML")
                    except:
                        pass
            except:
                pass
    conn.close()

# ==================== GLOBAL STATES ====================
user_temp_sessions = {}
user_instagram_state = {}
user_firebase_state = {}

# ==================== TEMP MAIL CLASS (unchanged) ====================
class TempMailBot:
    # ... (keep the same as original)
    pass

# ==================== FLIPKART CHECKER (unchanged) ====================
def check_flipkart(num):
    # ... (keep the same)
    pass

# ==================== INSTAGRAM DOWNLOADER (unchanged) ====================
L = instaloader.Instaloader(...)
def download_reel(url):
    # ...
    pass

def download_bulk(urls):
    # ...
    pass

# ==================== APK ANALYSIS (unchanged) ====================
def get_md5(file_path): ...
def extract_strings_from_dex_files(apk_path): ...
def extract_from_manifest(apk_path): ...
def get_package_info(apk_path): ...
def search_in_strings(strings_list): ...
def analyze_apk(apk_path): ...
def format_results(results, apk_path, file_size, num_dex_strings): ...

# ==================== SAFE HANDLER DECORATOR ====================
def safe_handler(func):
    def wrapper(message_or_call, *args, **kwargs):
        try:
            return func(message_or_call, *args, **kwargs)
        except Exception as e:
            logger.error(f"Handler error: {e}", exc_info=True)
            try:
                if hasattr(message_or_call, 'chat'):
                    bot.reply_to(message_or_call, f"⚠️ Internal error: {str(e)[:200]}")
                elif hasattr(message_or_call, 'message'):
                    bot.send_message(message_or_call.message.chat.id, f"⚠️ Internal error: {str(e)[:200]}")
                else:
                    logger.warning("Cannot send error reply: no chat context")
            except:
                pass
    return wrapper

# ==================== ALL HANDLERS (wrapped with @safe_handler) ====================

# ---------- START ----------
@bot.message_handler(commands=['start'])
@safe_handler
def start_cmd(message):
    # ... (use original logic but with safe_db_query already used)
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

# ---------- PING (for testing) ----------
@bot.message_handler(commands=['ping'])
@safe_handler
def ping_cmd(message):
    bot.reply_to(message, "🏓 Pong! Bot is alive and responding.")

# ---------- VERIFY CALLBACK ----------
@bot.callback_query_handler(func=lambda call: call.data == "verify_membership")
@safe_handler
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

# ---------- MODULE NAVIGATION ----------
@bot.callback_query_handler(func=lambda call: call.data.startswith("module_"))
@safe_handler
def handle_module_callback(call):
    module = call.data.split("_")[1]
    user_id = call.from_user.id
    balance = get_user_balance(user_id)

    if module not in ["referral", "admin"]:
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
    elif module == "admin":
        if call.from_user.id != ADMIN_ID:
            bot.answer_callback_query(call.id, "⛔ Admin only!")
            return
        bot.delete_message(call.message.chat.id, call.message.message_id)
        text = admin_panel_text()
        bot.send_message(call.message.chat.id, text, reply_markup=admin_panel_keyboard(), parse_mode="HTML")
        bot.answer_callback_query(call.id)

# ---------- REFERRAL CALLBACKS ----------
@bot.callback_query_handler(func=lambda call: call.data.startswith("referral_"))
@safe_handler
def handle_referral_callback(call):
    action = call.data.split("_")[2] if len(call.data.split("_")) > 2 else call.data.split("_")[1]
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    msg_id = call.message.message_id

    if action == "get_link":
        if not check_membership(user_id):
            bot.answer_callback_query(call.id, "❌ Please join channel and group first!", show_alert=True)
            return
        link = get_referral_link(user_id)
        bot.answer_callback_query(call.id, "🔗 Link copied! Share it with friends.")
        bot.edit_message_text(
            f"🔗 <b>Your Referral Link</b>\n\n<code>{link}</code>\n\n📤 Share this link with your friends!\n🎁 You get <b>+{REFERRAL_BONUS} Credits</b> per referral (after 24h).\n🎁 Your friend gets <b>+{NEW_USER_BONUS} Credits</b> on joining.\n\n⚠️ Make sure your friend joins both channel and group!",
            chat_id=chat_id, message_id=msg_id, reply_markup=referral_menu_keyboard(), parse_mode="HTML"
        )
    elif action == "stats":
        referral_count = get_referral_count(user_id)
        pending_count = get_pending_referral_count(user_id)
        bot.answer_callback_query(call.id, "📊 Fetching your stats...")
        bot.edit_message_text(
            f"📊 <b>Your Referral Stats</b>\n\n👥 Confirmed Referrals: <b>{referral_count}</b>\n⏳ Pending (24h): <b>{pending_count}</b>\n💰 Bonus per referral: <b>+{REFERRAL_BONUS} Credits</b>\n🎁 New user bonus: <b>+{NEW_USER_BONUS} Credits</b>\n\n💡 Referrals are confirmed after 24 hours of stay in our community.",
            chat_id=chat_id, message_id=msg_id, reply_markup=referral_menu_keyboard(), parse_mode="HTML"
        )

# ---------- FIREBASE CALLBACKS ----------
@bot.callback_query_handler(func=lambda call: call.data.startswith("firebase_"))
@safe_handler
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
            "📤 <b>Send APK</b>\n\nPlease upload your APK file.\nI will analyze it for Firebase credentials and other sensitive data.\n\n⏱️ Analysis may take 30-60 seconds.\n💰 Cost: 2 Credits.\nClick <b>Remove APK</b> to cancel.",
            chat_id=chat_id, message_id=msg_id, reply_markup=firebase_menu_keyboard(), parse_mode="HTML"
        )
    elif action == "remove":
        user_firebase_state[user_id] = False
        bot.answer_callback_query(call.id, "🗑️ Firebase session cleared.")
        bot.edit_message_text(
            "🗑️ <b>APK Removed</b>\n\nAny pending APK upload has been cleared.\nYou can send a new APK anytime.",
            chat_id=chat_id, message_id=msg_id, reply_markup=firebase_menu_keyboard(), parse_mode="HTML"
        )

# ---------- APK HANDLER ----------
@bot.message_handler(content_types=['document'])
@safe_handler
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
            chat_id=message.chat.id, message_id=processing_msg.message_id, parse_mode="HTML"
        )
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except:
                pass

# ---------- SHOPSY CALLBACKS ----------
@bot.callback_query_handler(func=lambda call: call.data.startswith("shopsy_"))
@safe_handler
def handle_shopsy_callback(call):
    action = call.data.split("_")[1]
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    msg_id = call.message.message_id
    balance, status = get_user_balance(user_id), "ACTIVE"

    if action == "start":
        if balance < 1:
            bot.answer_callback_query(call.id, "❌ Insufficient credits!")
            bot.edit_message_text(
                "❌ <b>Insufficient credits!</b>\n\nYou need at least 1 credit to run a task.",
                chat_id=chat_id, message_id=msg_id, reply_markup=shopsy_menu_keyboard(), parse_mode="HTML"
            )
            return
        update_user_balance(user_id, -1)
        bot.answer_callback_query(call.id, "✅ Task started!")
        bot.delete_message(chat_id, msg_id)
        new_balance = get_user_balance(user_id)
        new_text = shopsy_menu_text(user_id, new_balance, status)
        bot.send_message(chat_id, new_text, reply_markup=shopsy_menu_keyboard(), parse_mode="HTML")
    elif action == "accounts":
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            "📁 <b>My Accounts</b>\n\nYou have <b>1</b> account linked:\n• +91 9826621729 (Default)\n\nTo add more accounts, contact support.",
            chat_id=chat_id, message_id=msg_id, reply_markup=shopsy_menu_keyboard(), parse_mode="HTML"
        )
    elif action == "howto":
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            "❓ <b>How To Use Shopsy Auto-Mine</b>\n\n1️⃣ Click <b>Start New Task</b> – bot will mine 30 Shopsy coins.\n2️⃣ Each run costs <b>1 Credit</b>.\n3️⃣ You need a valid Shopsy account (phone+OTP).\n4️⃣ Credits can be earned via referrals or tasks.\n\n⚠️ Make sure you have sufficient balance before starting.",
            chat_id=chat_id, message_id=msg_id, reply_markup=shopsy_menu_keyboard(), parse_mode="HTML"
        )

# ---------- TEMP CALLBACKS ----------
@bot.callback_query_handler(func=lambda call: call.data.startswith("temp_"))
@safe_handler
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
                f"📧 <b>New Email Created!</b>\n\n📧 <b>Email:</b> <code>{result['email']}</code>\n⏱️ <b>Expires:</b> 10 minutes\n\n💡 Use <b>Check Inbox</b> to see messages\n🔑 Use <b>Get OTP</b> to auto-detect OTP\n\n<i>Powered By Viediet Utility</i>",
                chat_id=chat_id, message_id=msg_id, reply_markup=temp_menu_keyboard(), parse_mode="HTML"
            )
        else:
            bot.answer_callback_query(call.id, "❌ Failed to create email!", show_alert=True)
            bot.edit_message_text(
                f"❌ <b>Failed!</b>\n\nError: {result.get('error', 'Unknown')}",
                chat_id=chat_id, message_id=msg_id, reply_markup=temp_menu_keyboard(), parse_mode="HTML"
            )
    # ... (other temp actions: inbox, otp, delete) – I'm truncating for brevity, but they remain the same.

# ---------- FLIPKART PHONE HANDLER ----------
@bot.message_handler(func=lambda message: message.text and message.text.isdigit() and len(message.text) == 10)
@safe_handler
def handle_phone_number(message):
    user_id = message.from_user.id
    balance = get_user_balance(user_id)
    if balance < 1:
        bot.reply_to(message, "❌ Insufficient credits! You need 1 credit to check a number.")
        return
    update_user_balance(user_id, -1)
    processing = bot.reply_to(message, f"🔍 Checking <code>{message.text}</code> on Flipkart...", parse_mode="HTML")
    def check_thread():
        try:
            result = check_flipkart(message.text)
            new_balance = get_user_balance(user_id)
            bot.edit_message_text(
                f"📱 <b>Result for {message.text}</b>\n\n{result}\n\n💰 Remaining Credits: {new_balance}",
                chat_id=message.chat.id, message_id=processing.message_id, parse_mode="HTML"
            )
            log_usage(user_id, "Flipkart Checker", f"Number: {message.text}")
        except Exception as e:
            bot.edit_message_text(f"❌ Error: {str(e)}", chat_id=message.chat.id, message_id=processing.message_id)
    threading.Thread(target=check_thread).start()

# ---------- INSTAGRAM HANDLERS ----------
@bot.callback_query_handler(func=lambda call: call.data.startswith("instagram_"))
@safe_handler
def handle_instagram_callback(call):
    action = call.data.split("_")[1]
    user_id = call.from_user.id

    if action == "single":
        user_instagram_state[user_id] = "single"
        bot.answer_callback_query(call.id, "📹 Send a single Instagram video URL.")
        bot.edit_message_text(
            "📹 <b>Single Download</b>\n\nSend me the Instagram video link.\nExample: <code>https://www.instagram.com/reel/xyz123/</code>\n\n💡 Costs 1 Credit.\n\n<i>Powered By Viediet Utility</i>",
            chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=instagram_menu_keyboard(), parse_mode="HTML"
        )
    elif action == "bulk":
        user_instagram_state[user_id] = "bulk"
        bot.answer_callback_query(call.id, "📚 Send multiple Instagram video URLs (one per line).")
        bot.edit_message_text(
            "📚 <b>Bulk Download</b>\n\nSend me multiple Instagram video links,\neach on a new line.\n\nExample:\n<code>https://www.instagram.com/reel/abc/\nhttps://www.instagram.com/reel/def/</code>\n\n💡 Costs 1 Credit per video.\n\n<i>Powered By Viediet Utility</i>",
            chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=instagram_menu_keyboard(), parse_mode="HTML"
        )

@bot.message_handler(func=lambda message: message.text and 'instagram.com' in message.text.lower())
@safe_handler
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
            try:
                file_path = download_reel(urls[0])
                if file_path:
                    with open(file_path, "rb") as vid:
                        bot.send_video(message.chat.id, vid, caption="✅ Downloaded successfully!")
                    os.remove(file_path)
                    shutil.rmtree(os.path.dirname(file_path), ignore_errors=True)
                else:
                    bot.send_message(message.chat.id, "❌ Failed to download reel. Check URL or try again.")
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ Download error: {str(e)}")
            finally:
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
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ Bulk download error: {str(e)}")
            finally:
                bot.delete_message(message.chat.id, processing.message_id)
        threading.Thread(target=download_bulk_thread).start()

    user_instagram_state[user_id] = None

# ---------- ADMIN COMMANDS ----------
@bot.message_handler(commands=['addcoins'])
@safe_handler
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
        conn = get_db_connection()
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
@safe_handler
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
        conn = get_db_connection()
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
@safe_handler
def broadcast_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⛔ Admin only!")
        return
    msg = message.text.replace('/broadcast', '', 1).strip()
    if not msg:
        bot.reply_to(message, "❌ Please provide a message to broadcast.")
        return
    conn = get_db_connection()
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
@safe_handler
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

# ---------- ADMIN PANEL CALLBACKS ----------
@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
@safe_handler
def handle_admin_callback(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "⛔ Admin only!")
        return
    action = call.data.split("_")[1]
    chat_id = call.message.chat.id
    msg_id = call.message.message_id

    if action == "stats":
        total_users = get_total_users()
        total_coins = get_total_coins()
        total_usage = get_total_usage()
        bot.edit_message_text(
            f"📊 <b>Bot Statistics</b>\n\n👥 Total Users: <b>{total_users}</b>\n💰 Total Coins: <b>{total_coins}</b>\n📈 Total Usage: <b>{total_usage}</b> operations\n🔢 Admin ID: <code>{ADMIN_ID}</code>",
            chat_id=chat_id, message_id=msg_id, reply_markup=admin_panel_keyboard(), parse_mode="HTML"
        )
        bot.answer_callback_query(call.id)
    elif action == "users":
        users = get_all_users()
        if not users:
            msg = "No users found."
        else:
            msg = "👥 <b>User List (Top 20 by coins)</b>\n\n"
            for i, (uid, uname, bal, stat) in enumerate(users[:20], 1):
                msg += f"{i}. <code>{uname}</code> (ID: {uid}) – {bal} coins [{stat}]\n"
        bot.edit_message_text(msg, chat_id=chat_id, message_id=msg_id, reply_markup=admin_panel_keyboard(), parse_mode="HTML")
        bot.answer_callback_query(call.id)
    elif action == "add_coins":
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            "➕ <b>Add Coins</b>\n\nSend message in format:\n`/addcoins @username amount`\nor\n`/addcoins user_id amount`\n\nExample: `/addcoins @Viediet 50`",
            chat_id=chat_id, message_id=msg_id, reply_markup=admin_panel_keyboard(), parse_mode="HTML"
        )
    elif action == "remove_coins":
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            "➖ <b>Remove Coins</b>\n\nSend message in format:\n`/removecoins @username amount`\nor\n`/removecoins user_id amount`\n\nExample: `/removecoins @Viediet 20`",
            chat_id=chat_id, message_id=msg_id, reply_markup=admin_panel_keyboard(), parse_mode="HTML"
        )
    elif action == "broadcast":
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            "📢 <b>Broadcast</b>\n\nSend a message to all users.\nFormat: `/broadcast your message here`\n\nExample: `/broadcast Hello everyone!`",
            chat_id=chat_id, message_id=msg_id, reply_markup=admin_panel_keyboard(), parse_mode="HTML"
        )
    elif action == "costs":
        current_cost = get_config("firebase_cost", "2")
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            f"⚙️ <b>Set Costs</b>\n\nCurrent Firebase cost: <code>{current_cost}</code> credits\n\nTo change, send:\n`/setcost firebase 5`\n\n(Other modules can be added later)",
            chat_id=chat_id, message_id=msg_id, reply_markup=admin_panel_keyboard(), parse_mode="HTML"
        )

# ---------- BACK TO MAIN ----------
@bot.callback_query_handler(func=lambda call: call.data == "back_menu")
@safe_handler
def back_to_menu(call):
    user = call.from_user
    user_id = user.id
    balance = get_user_balance(user_id)
    is_admin = (user_id == ADMIN_ID)
    text = main_menu_text(user_id, user.first_name, balance, "ACTIVE")
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, text, reply_markup=main_menu_keyboard(is_admin), parse_mode="HTML")
    bot.answer_callback_query(call.id)

# ---------- FALLBACK ----------
@bot.message_handler(func=lambda m: True)
@safe_handler
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
    logger.info("🤖 Bot starting with full fixes...")
    # Remove webhook
    try:
        bot.remove_webhook()
        time.sleep(2)
    except Exception as e:
        logger.warning(f"Webhook removal failed: {e}")

    # Start referral checker thread
    threading.Thread(target=run_scheduled_tasks, daemon=True).start()

    # Polling loop with auto-restart
    while True:
        try:
            bot.polling(non_stop=True, interval=0, timeout=30)
        except Exception as e:
            logger.error(f"Polling error: {e}")
            time.sleep(5)
