#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# NRTECNO SYSTEM - FIREBASE EXTRACTOR - FULLY FIXED

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
import shutil
import tempfile
import hashlib
import zipfile
import sqlite3
import uuid
from datetime import datetime, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ==================== CONFIG ====================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    logging.error("BOT_TOKEN environment variable not set.")
    exit(1)

ADMIN_ID = int(os.environ.get("ADMIN_ID", 1364476174))
CHANNEL_USERNAME = "viedietlooters"
NEW_USER_BONUS = 5
FIREBASE_COST = 2

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

DB_PATH = "viediet_bot.db"

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
        referral_code TEXT UNIQUE
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS usage_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        module TEXT,
        details TEXT,
        timestamp TEXT
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
            'last_used': row[6], 'referred_by': row[7], 'referral_code': row[8]
        }
    return None

def create_user(user_id, username, first_name):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    now = datetime.now().isoformat()
    ref_code = f"REF{user_id}{random.randint(1000, 9999)}"
    c.execute('''INSERT OR IGNORE INTO users 
        (user_id, username, first_name, balance, status, registered_at, last_used, referral_code)
        VALUES (?, ?, ?, ?, 'ACTIVE', ?, ?, ?)''',
        (user_id, username, first_name, NEW_USER_BONUS, now, now, ref_code))
    conn.commit()
    conn.close()
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

def log_usage(user_id, module, details=""):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute('INSERT INTO usage_logs (user_id, module, details, timestamp) VALUES (?, ?, ?, ?)',
              (user_id, module, details, now))
    c.execute('UPDATE users SET last_used = ? WHERE user_id = ?', (now, user_id))
    conn.commit()
    conn.close()

# ==================== MEMBERSHIP ====================
def is_channel_member(user_id):
    try:
        member = bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# ==================== GLOBAL STATES ====================
user_firebase_state = {}

# ==================== MAIN MENU ====================
def main_menu_text(user_id, first_name, balance, status):
    return f"""
╔══════════════════════════════════╗
║     🚀 VIEDIET UTILITY BOT      ║
╚══════════════════════════════════╝

👋 Welcome back, <b>{first_name}</b>!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 <b>Balance:</b> <code>{balance}</code> Credits
👤 <b>User ID:</b> <code>{user_id}</code>
📊 <b>Status:</b> {status}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>⚡ Available Module:</b>
• 🔥 Firebase Extractor - Extract credentials from APK

<b>💡 Pro Tip:</b> Earn free credits by referring friends!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<i>Made with ❤️ by @viedietextraa</i>
"""

def main_menu_keyboard(is_admin=False):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.row(InlineKeyboardButton("🔥 Firebase Extractor", callback_data="module_firebase"))
    kb.row(InlineKeyboardButton("📊 Stats", callback_data="module_stats"))
    if is_admin:
        kb.row(InlineKeyboardButton("👑 Admin", callback_data="module_admin"))
    return kb

def firebase_menu_text(user_id, balance, status, cost):
    return f"""
╔══════════════════════════════════╗
║     🔥 FIREBASE EXTRACTOR       ║
╚══════════════════════════════════╝

<b>📋 Module:</b> Firebase Extractor
<b>💰 Cost:</b> <code>{cost}</code> Credits
<b>💳 Balance:</b> <code>{balance}</code> Credits

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>📌 What it does:</b>
Extracts sensitive data from APK files:
• 🔥 Firebase URLs & Database endpoints
• 🔑 API Keys (Google, Firebase, etc.)
• 🔐 Secrets & Tokens
• 📦 Storage Buckets
• 📄 JSON Endpoints

<b>📤 How to use:</b>
1. Click <b>📤 Send APK</b>
2. Upload your APK file
3. Wait for analysis (30-60 sec)
4. Get extracted credentials

<b>⚠️ Warning:</b>
Only use on APKs you own!
"""

def firebase_menu_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.row(
        InlineKeyboardButton("📤 Send APK", callback_data="firebase_send"),
        InlineKeyboardButton("🗑️ Remove APK", callback_data="firebase_remove")
    )
    kb.row(InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu"))
    return kb

def back_button():
    kb = InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu"))
    return kb

# ==================== FIREBASE EXTRACTOR FUNCTIONS ====================
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
    out.append("⚠️ <i>DO NOT test without permission</i>")
    
    return "\n".join(out)

# ==================== START COMMAND ====================
@bot.message_handler(commands=['start'])
def start_cmd(message):
    user = message.from_user
    user_id = user.id
    username = user.username or "NoUsername"
    first_name = user.first_name or "User"
    
    existing = get_user(user_id)
    if not existing:
        create_user(user_id, username, first_name)
    
    if not is_channel_member(user_id):
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
    if is_channel_member(user_id):
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
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    bot.send_message(call.message.chat.id, text, reply_markup=main_menu_keyboard(is_admin), parse_mode="HTML")
    bot.answer_callback_query(call.id)

# ==================== MODULE NAVIGATION ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith("module_"))
def handle_module_callback(call):
    module = call.data.split("_")[1]
    user_id = call.from_user.id
    balance = get_user_balance(user_id)

    if module == "firebase":
        if not is_channel_member(user_id):
            bot.answer_callback_query(call.id, "❌ Please join channel first!", show_alert=True)
            return
        text = firebase_menu_text(user_id, balance, "ACTIVE", FIREBASE_COST)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        bot.send_message(call.message.chat.id, text, reply_markup=firebase_menu_keyboard(), parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif module == "stats":
        total_users = get_total_users()
        total_coins = get_total_coins()
        total_usage = get_total_usage()
        bot.answer_callback_query(
            call.id, 
            f"📊 Users: {total_users} | Coins: {total_coins} | Usage: {total_usage}",
            show_alert=True
        )

    elif module == "admin":
        if user_id == ADMIN_ID:
            bot.answer_callback_query(call.id, "👑 Admin panel coming soon!")
        else:
            bot.answer_callback_query(call.id, "⛔ Admin only!")

# ==================== FIREBASE CALLBACKS ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith("firebase_"))
def handle_firebase_callback(call):
    action = call.data.split("_")[1]
    user_id = call.from_user.id
    balance = get_user_balance(user_id)

    if action == "send":
        if not is_channel_member(user_id):
            bot.answer_callback_query(call.id, "❌ Please join channel first!", show_alert=True)
            return
        
        if balance < FIREBASE_COST:
            bot.answer_callback_query(call.id, f"❌ You need {FIREBASE_COST} credits!", show_alert=True)
            return
        
        user_firebase_state[user_id] = True
        bot.answer_callback_query(call.id, "📤 Ready! Send your APK file.")
        
        kb = InlineKeyboardMarkup(row_width=1)
        kb.row(InlineKeyboardButton("❌ Cancel", callback_data="firebase_abort"))
        kb.row(InlineKeyboardButton("🔙 Back", callback_data="back_menu"))
        
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        
        bot.send_message(
            call.message.chat.id,
            f"📤 <b>Send APK</b>\n\n"
            f"Please upload your APK file.\n"
            f"I will analyze it for Firebase credentials.\n\n"
            f"⏱️ Analysis: 30-60 seconds\n"
            f"💰 Cost: {FIREBASE_COST} Credits\n\n"
            f"Send <b>/cancel</b> to abort.",
            reply_markup=kb,
            parse_mode="HTML"
        )

    elif action == "remove":
        user_firebase_state[user_id] = False
        bot.answer_callback_query(call.id, "🗑️ Firebase session cleared.")
        text = firebase_menu_text(user_id, balance, "ACTIVE", FIREBASE_COST)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        bot.send_message(call.message.chat.id, text, reply_markup=firebase_menu_keyboard(), parse_mode="HTML")

    elif action == "abort":
        user_firebase_state[user_id] = False
        bot.answer_callback_query(call.id, "❌ Firebase extraction cancelled.")
        text = firebase_menu_text(user_id, balance, "ACTIVE", FIREBASE_COST)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        bot.send_message(call.message.chat.id, text, reply_markup=firebase_menu_keyboard(), parse_mode="HTML")

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

    balance = get_user_balance(user_id)
    if balance < FIREBASE_COST:
        bot.reply_to(message, f"❌ Insufficient credits! Need {FIREBASE_COST} credits. Balance: {balance}")
        user_firebase_state[user_id] = False
        return

    update_user_balance(user_id, -FIREBASE_COST)
    processing_msg = bot.reply_to(
        message, 
        "⏳ <b>Analyzing APK...</b>\n\n"
        "🔍 Scanning for credentials...\n"
        "⏱️ This may take 30-60 seconds.",
        parse_mode="HTML"
    )

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
        
        bot.edit_message_text(
            reply,
            chat_id=message.chat.id,
            message_id=processing_msg.message_id,
            parse_mode="HTML",
            reply_markup=back_button()
        )
        log_usage(user_id, "Firebase Extractor", f"APK: {doc.file_name}")
        
    except Exception as e:
        logger.error(f"APK analysis error: {e}")
        update_user_balance(user_id, FIREBASE_COST)
        bot.edit_message_text(
            f"❌ <b>Analysis failed!</b>\n\nError: {str(e)[:200]}",
            chat_id=message.chat.id,
            message_id=processing_msg.message_id,
            parse_mode="HTML",
            reply_markup=back_button()
        )
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except:
                pass
        user_firebase_state[user_id] = False

# ==================== STATS FUNCTIONS ====================
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

# ==================== CANCEL COMMAND ====================
@bot.message_handler(commands=['cancel'])
def cancel_cmd(message):
    user_id = message.from_user.id
    if user_firebase_state.get(user_id):
        user_firebase_state[user_id] = False
        bot.reply_to(message, "❌ Firebase upload cancelled.", reply_markup=back_button())
    else:
        bot.reply_to(message, "No active operation to cancel.")

# ==================== FALLBACK ====================
@bot.message_handler(func=lambda m: True)
def fallback(message):
    bot.reply_to(message, "❓ Unknown command. Use /start to see the menu.")

# ==================== MAIN ====================
if __name__ == "__main__":
    logger.info("🤖 Bot started – FIREBASE EXTRACTOR ONLY!")
    logger.info("💳 Cost: 2 Credits per analysis")
    logger.info("📤 Send APK files to extract credentials")
    
    try:
        bot.remove_webhook()
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
