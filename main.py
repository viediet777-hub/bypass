#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# NRTECNO SYSTEM - VIEDIET BOT v3.0
# REMOVED: Shopsy, Yoga, Slay features

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
import sqlite3
import hashlib
import subprocess
from datetime import datetime, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

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
        help_menu_text,
        igviewer_menu_text, igviewer_menu_keyboard
    )
except ImportError:
    def main_menu_text(u, f, b, s): return f"Welcome {f}! Balance: {b}"
    def main_menu_keyboard(a=False): 
        kb = InlineKeyboardMarkup(row_width=1)
        kb.row(InlineKeyboardButton("📊 Stats", callback_data="module_stats"))
        return kb

# ==================== CONFIG ====================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    logging.error("BOT_TOKEN environment variable not set.")
    exit(1)

ADMIN_ID = int(os.environ.get("ADMIN_ID", 1364476174))
CHANNEL_USERNAME = "viedietlooters"

# Credit System
NEW_USER_BONUS = 0
REFERRAL_BONUS = 3
REFERRAL_STAY_HOURS = 0

DEFAULT_COSTS = {
    "firebase": 1,
    "flipkart": 1,
    "instagram_single": 1,
    "instagram_bulk": 1,
    "igviewer": 1,
}

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
        balance INTEGER DEFAULT 0,
        status TEXT DEFAULT 'ACTIVE',
        registered_at TEXT,
        last_used TEXT,
        referred_by INTEGER DEFAULT NULL,
        referral_code TEXT UNIQUE,
        account_age_days INTEGER DEFAULT 0,
        is_valid INTEGER DEFAULT 1,
        ip_address TEXT DEFAULT NULL,
        last_check TEXT DEFAULT NULL
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
            'last_check': row[12]
        }
    return None

def create_user(user_id, username, first_name, referred_by=None, ip_address=None):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    now = datetime.now().isoformat()
    ref_code = f"REF{user_id}{random.randint(1000, 9999)}"
    
    c.execute('''INSERT OR IGNORE INTO users 
        (user_id, username, first_name, balance, status, registered_at, last_used, referred_by, referral_code, ip_address)
        VALUES (?, ?, ?, 0, 'ACTIVE', ?, ?, ?, ?, ?)''',
        (user_id, username, first_name, now, now, referred_by, ref_code, ip_address))
    conn.commit()
    conn.close()
    
    if referred_by:
        add_pending_referral(referred_by, user_id)
    return 0

def update_user_balance(user_id, delta):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (delta, user_id))
    conn.commit()
    conn.close()

def get_user_balance(user_id):
    user = get_user(user_id)
    return user['balance'] if user else 0

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

# ==================== REFERRAL CHECK ====================
def check_and_award_referrals():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    now = datetime.now()
    
    c.execute('SELECT id, referrer_id, referred_id, join_timestamp FROM pending_referrals')
    pending = c.fetchall()
    
    for pid, referrer_id, referred_id, join_ts in pending:
        try:
            join_time = datetime.fromisoformat(join_ts)
            if (now - join_time) >= timedelta(hours=REFERRAL_STAY_HOURS):
                c.execute('SELECT is_valid FROM users WHERE user_id = ?', (referred_id,))
                user_row = c.fetchone()
                if user_row and user_row[0] == 1:
                    update_user_balance(referrer_id, REFERRAL_BONUS)
                    c.execute('INSERT INTO referrals (referrer_id, referred_id, join_timestamp, points_awarded, is_valid) VALUES (?, ?, ?, ?, 1)',
                              (referrer_id, referred_id, join_ts, REFERRAL_BONUS))
                    c.execute('DELETE FROM pending_referrals WHERE id = ?', (pid,))
                    conn.commit()
                    try:
                        bot.send_message(referrer_id, f"🎉 <b>Referral Bonus!</b>\n\nYou earned <b>+{REFERRAL_BONUS} Credits</b> for referring a user!\n💰 New balance: {get_user_balance(referrer_id)}", parse_mode="HTML")
                    except:
                        pass
        except Exception as e:
            logger.error(f"Referral award error: {e}")
    
    conn.close()

def run_scheduled_tasks():
    while True:
        try:
            check_and_award_referrals()
            logger.info("[SCHEDULED] Referral check completed")
        except Exception as e:
            logger.error(f"[SCHEDULED] Referral check error: {e}")
        time.sleep(60)

# ==================== BACK BUTTON ====================
def back_button():
    kb = InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu"))
    return kb

# ==================== MEMBERSHIP CHECK ====================
def check_membership(user_id):
    try:
        member = bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

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

# ==================== ADMIN COMMANDS ====================
@bot.message_handler(commands=['addcoins'])
def addcoins_command(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, "❌ Unauthorized! Admin only.")
        return
    
    try:
        parts = message.text.strip().split()
        if len(parts) == 2:
            amount = int(parts[1])
            if amount <= 0:
                bot.reply_to(message, "❌ Amount must be positive!")
                return
            
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute('UPDATE users SET balance = balance + ?', (amount,))
            affected = c.rowcount
            conn.commit()
            conn.close()
            
            bot.reply_to(
                message,
                f"✅ <b>Added {amount} Credits to ALL Users!</b>\n\n"
                f"👥 Affected: <code>{affected}</code> users",
                parse_mode="HTML"
            )
            return
        
        elif len(parts) == 3:
            target_id = int(parts[1])
            amount = int(parts[2])
            
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
                    f"➕ <code>+{amount} Credits</code> added.\n"
                    f"💰 New Balance: <code>{new_balance}</code>",
                    parse_mode="HTML"
                )
            except:
                pass
            return
        
        else:
            bot.reply_to(
                message,
                "❌ <b>Invalid format!</b>\n\n"
                "1️⃣ Add to ALL: <code>/addcoins AMOUNT</code>\n"
                "2️⃣ Add to specific: <code>/addcoins USER_ID AMOUNT</code>",
                parse_mode="HTML"
            )
            
    except ValueError:
        bot.reply_to(message, "❌ Invalid number format!")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)[:100]}")

@bot.message_handler(commands=['removecoins'])
def removecoins_command(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, "❌ Unauthorized! Admin only.")
        return
    
    try:
        parts = message.text.strip().split()
        if len(parts) == 2:
            amount = int(parts[1])
            if amount <= 0:
                bot.reply_to(message, "❌ Amount must be positive!")
                return
            
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute('UPDATE users SET balance = balance - ? WHERE balance >= ?', (amount, amount))
            affected = c.rowcount
            conn.commit()
            conn.close()
            
            bot.reply_to(
                message,
                f"✅ <b>Removed {amount} Credits from ALL Users!</b>\n\n"
                f"👥 Affected: <code>{affected}</code> users",
                parse_mode="HTML"
            )
            return
        
        elif len(parts) == 3:
            target_id = int(parts[1])
            amount = int(parts[2])
            
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
                    f"❌ User has insufficient balance!\nCurrent: <code>{current_balance}</code>",
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
                    f"➖ <code>-{amount} Credits</code> removed.\n"
                    f"💰 New Balance: <code>{new_balance}</code>",
                    parse_mode="HTML"
                )
            except:
                pass
            return
        
        else:
            bot.reply_to(
                message,
                "❌ <b>Invalid format!</b>\n\n"
                "1️⃣ Remove from ALL: <code>/removecoins AMOUNT</code>\n"
                "2️⃣ Remove from specific: <code>/removecoins USER_ID AMOUNT</code>",
                parse_mode="HTML"
            )
            
    except ValueError:
        bot.reply_to(message, "❌ Invalid number format!")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)[:100]}")

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
                "Example: <code>/setcost flipkart 2</code>\n\n"
                "Available modules: firebase, flipkart, instagram_single, instagram_bulk, igviewer",
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

@bot.message_handler(commands=['broadcast'])
def broadcast_command(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, "❌ Unauthorized!")
        return
    
    msg = bot.reply_to(
        message,
        "📢 <b>Broadcast Message</b>\n\n"
        "Send the message you want to broadcast to all users.\n\n"
        "⚠️ <b>Warning:</b> This will send to ALL users!\n\n"
        "Send /cancel to abort.",
        parse_mode="HTML"
    )
    bot.register_next_step_handler(msg, broadcast_handler)

def broadcast_handler(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
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
    
    success = 0
    failed = 0
    
    status_msg = bot.reply_to(message, f"📢 Broadcasting to {len(users)} users...")
    
    for uid, in users:
        try:
            bot.send_message(uid, f"📢 <b>Announcement</b>\n\n{message.text}", parse_mode="HTML")
            success += 1
            time.sleep(0.05)
        except:
            failed += 1
    
    bot.edit_message_text(
        f"✅ <b>Broadcast Complete!</b>\n\n"
        f"✅ Sent: <code>{success}</code>\n"
        f"❌ Failed: <code>{failed}</code>",
        chat_id=message.chat.id,
        message_id=status_msg.message_id,
        parse_mode="HTML"
    )

# ==================== CALLBACK HANDLER ====================
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
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute('SELECT COUNT(*) FROM users')
            total_users = c.fetchone()[0]
            c.execute('SELECT SUM(balance) FROM users')
            total_coins = c.fetchone()[0] or 0
            c.execute('SELECT COUNT(*) FROM usage_logs')
            total_usage = c.fetchone()[0]
            conn.close()
            bot.answer_callback_query(
                call.id,
                f"📊 Stats:\n👥 Users: {total_users}\n💰 Coins: {total_coins}\n📈 Usage: {total_usage}",
                show_alert=True
            )
        else:
            bot.answer_callback_query(call.id, "Module not found")
        
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
            f"Share this link with friends and earn credits when they join!\n\n"
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
    
    # ===== ADMIN CALLBACKS =====
    if data.startswith("admin_"):
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ Unauthorized - Admin only!")
            return
        
        action = data.replace("admin_", "")
        
        if action == "stats":
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
            bot.send_message(
                call.message.chat.id,
                "💰 <b>Add Credits</b>\n\n"
                "<b>Usage:</b>\n"
                "1️⃣ Add to ALL users:\n"
                "<code>/addcoins AMOUNT</code>\n"
                "Example: <code>/addcoins 5</code>\n\n"
                "2️⃣ Add to specific user:\n"
                "<code>/addcoins USER_ID AMOUNT</code>\n"
                "Example: <code>/addcoins 123456789 10</code>",
                parse_mode="HTML"
            )
            bot.answer_callback_query(call.id)
            return
        
        if action == "remove_coins":
            bot.send_message(
                call.message.chat.id,
                "➖ <b>Remove Credits</b>\n\n"
                "<b>Usage:</b>\n"
                "1️⃣ Remove from ALL users:\n"
                "<code>/removecoins AMOUNT</code>\n"
                "Example: <code>/removecoins 5</code>\n\n"
                "2️⃣ Remove from specific user:\n"
                "<code>/removecoins USER_ID AMOUNT</code>\n"
                "Example: <code>/removecoins 123456789 10</code>",
                parse_mode="HTML"
            )
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
            bot.register_next_step_handler(msg, broadcast_handler)
            bot.answer_callback_query(call.id)
            return
        
        if action == "costs":
            costs_text = "⚙️ <b>Module Costs</b>\n\n"
            for module, default in DEFAULT_COSTS.items():
                current = get_module_cost(module)
                costs_text += f"• {module.title()}: <code>{current}</code> credits\n"
            
            costs_text += f"\n📝 To update: <code>/setcost MODULE AMOUNT</code>\n"
            costs_text += f"Example: <code>/setcost flipkart 2</code>"
            
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

# ==================== GET REFERRAL LINK ====================
def get_referral_link(user_id):
    bot_username = bot.get_me().username
    return f"https://t.me/{bot_username}?start=ref_{user_id}"

# ==================== MAIN ====================
if __name__ == "__main__":
    task_thread = threading.Thread(target=run_scheduled_tasks, daemon=True)
    task_thread.start()
    
    logger.info("=" * 50)
    logger.info("🤖 VIEDIET BOT v3.0 STARTED")
    logger.info("=" * 50)
    logger.info("💰 New Users: 0 credits")
    logger.info("🔗 Referral: +3 credits per referral")
    logger.info("📱 Modules: Firebase, Temp Mail, Flipkart, Instagram, IG Viewer, Music")
    logger.info("👑 Admin: /addcoins, /removecoins, /setcost, /broadcast")
    logger.info("=" * 50)
    
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
