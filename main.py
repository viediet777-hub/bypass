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
from datetime import datetime, timedelta
from menu import (
    main_menu_text, main_menu_keyboard,
    shopsy_menu_text, shopsy_menu_keyboard,
    firebase_menu_text, firebase_menu_keyboard,
    temp_menu_text, temp_menu_keyboard,
    flipkart_menu_text, flipkart_menu_keyboard,
    instagram_menu_text, instagram_menu_keyboard   # 👈 ADD THIS
)

# ==================== CONFIG ====================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    BOT_TOKEN = "7893651923:AAF2VrYFQMn3pjek06fti6eTlHFVkj7AUWI"
    logging.warning("Using hardcoded token. Please set BOT_TOKEN environment variable on Railway.")

if not BOT_TOKEN or not BOT_TOKEN.startswith("789"):
    logging.error("Invalid BOT_TOKEN. Please check your token.")
    exit(1)

# ==================== LOGGING ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== BOT INIT ====================
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ==================== DATA STORE ====================
user_balances = {}
user_status = {}
user_temp_sessions = {}  # user_id -> TempMailBot instance

def get_user_data(user_id):
    if user_id not in user_balances:
        user_balances[user_id] = 15
        user_status[user_id] = "ACTIVE"
    return user_balances[user_id], user_status[user_id]

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
        """Generate a new temporary email"""
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
            
            return {
                'success': True,
                'email': address,
                'expires': '10 minutes'
            }
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
                # Store new messages
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

# ==================== HANDLERS ====================

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user = message.from_user
    user_id = user.id
    balance, status = get_user_data(user_id)
    text = main_menu_text(user_id, user.first_name, balance, status)
    bot.send_message(message.chat.id, text, reply_markup=main_menu_keyboard())

@bot.message_handler(commands=['ping'])
def ping_cmd(message):
    bot.reply_to(message, "🏓 Pong! Bot is alive.")

# ---------- Module Navigation ----------
@bot.callback_query_handler(func=lambda call: call.data.startswith("module_"))
def handle_module_callback(call):
    module = call.data.split("_")[1]
    user_id = call.from_user.id
    balance, status = get_user_data(user_id)

    if module == "shopsy":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        text = shopsy_menu_text(user_id, balance, status)
        bot.send_message(call.message.chat.id, text, reply_markup=shopsy_menu_keyboard(), parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif module == "firebase":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        text = firebase_menu_text(user_id, balance, status)
        bot.send_message(call.message.chat.id, text, reply_markup=firebase_menu_keyboard(), parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif module == "temp":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        text = temp_menu_text(user_id)
        bot.send_message(call.message.chat.id, text, reply_markup=temp_menu_keyboard(), parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif module == "flipkart":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        text = flipkart_menu_text(user_id, balance, status)
        bot.send_message(call.message.chat.id, text, reply_markup=flipkart_menu_keyboard(), parse_mode="HTML")
        bot.answer_callback_query(call.id)
    elif module == "instagram":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        text = instagram_menu_text(user_id, balance, status)
        bot.send_message(call.message.chat.id, text, reply_markup=instagram_menu_keyboard(), parse_mode="HTML")
        bot.answer_callback_query(call.id)
        
# ---------- Shopsy Callbacks ----------
@bot.callback_query_handler(func=lambda call: call.data.startswith("shopsy_"))
def handle_shopsy_callback(call):
    action = call.data.split("_")[1]
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    msg_id = call.message.message_id
    balance, status = get_user_data(user_id)

    if action == "start":
        if balance < 1:
            bot.answer_callback_query(call.id, "❌ Insufficient credits!")
            bot.edit_message_text(
                "❌ <b>Insufficient credits!</b>\n\nYou need at least 1 credit to run a task.",
                chat_id=chat_id, message_id=msg_id,
                reply_markup=shopsy_menu_keyboard(),
                parse_mode="HTML"
            )
            return
        user_balances[user_id] = balance - 1
        bot.answer_callback_query(call.id, "✅ Task started!")
        bot.delete_message(chat_id, msg_id)
        new_balance, _ = get_user_data(user_id)
        new_text = shopsy_menu_text(user_id, new_balance, status)
        bot.send_message(chat_id, new_text, reply_markup=shopsy_menu_keyboard(), parse_mode="HTML")

    elif action == "accounts":
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            "📁 <b>My Accounts</b>\n\nYou have <b>1</b> account linked:\n• +91 9826621729 (Default)\n\n"
            "To add more accounts, contact support.",
            chat_id=chat_id, message_id=msg_id,
            reply_markup=shopsy_menu_keyboard(),
            parse_mode="HTML"
        )

    elif action == "howto":
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            "❓ <b>How To Use Shopsy Auto-Mine</b>\n\n"
            "1️⃣ Click <b>Start New Task</b> – bot will mine 30 Shopsy coins.\n"
            "2️⃣ Each run costs <b>1 Credit</b>.\n"
            "3️⃣ You need a valid Shopsy account (phone+OTP).\n"
            "4️⃣ Credits can be earned via referrals or tasks.\n\n"
            "⚠️ Make sure you have sufficient balance before starting.",
            chat_id=chat_id, message_id=msg_id,
            reply_markup=shopsy_menu_keyboard(),
            parse_mode="HTML"
        )

# ---------- Firebase Callbacks (placeholder) ----------
@bot.callback_query_handler(func=lambda call: call.data.startswith("firebase_"))
def handle_firebase_callback(call):
    if call.data == "firebase_start":
        bot.answer_callback_query(call.id, "⏳ Firebase scanner coming soon...")
        bot.edit_message_text(
            "🔥 <b>Firebase Extractor</b>\n\n"
            "This feature is under development.\n"
            "Stay tuned for updates!",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=firebase_menu_keyboard(),
            parse_mode="HTML"
        )

# ---------- Temp Generator Callbacks ----------
@bot.callback_query_handler(func=lambda call: call.data.startswith("temp_"))
def handle_temp_callback(call):
    action = call.data.split("_")[1]
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    msg_id = call.message.message_id

    if action == "new":
        # Create new temp email
        if user_id in user_temp_sessions:
            # delete old session
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
        # Display latest 5 messages
        inbox_text = f"📥 <b>Inbox</b>\n\n"
        for i, msg in enumerate(messages[-5:], 1):
            from_addr = msg.get('from', {}).get('address', 'Unknown')
            subject = msg.get('subject', 'No Subject')
            inbox_text += f"━━━━━━━━━━━━━━━━━━━━\n"
            inbox_text += f"{i}. 📧 <b>From:</b> {from_addr}\n"
            inbox_text += f"   📝 <b>Subject:</b> {subject}\n"
            # Check if this message has OTP
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

# ---------- Flipkart Checker (placeholder) ----------
@bot.callback_query_handler(func=lambda call: call.data.startswith("flipkart_"))
def handle_flipkart_callback(call):
    pass

@bot.message_handler(func=lambda message: message.text and message.text.isdigit() and len(message.text) == 10)
def handle_phone_number(message):
    # Placeholder for Flipkart checker
    phone = message.text.strip()
    bot.reply_to(
        message,
        f"📱 <b>Checking phone number:</b> <code>{phone}</code>\n\n"
        f"This feature is under development.\n"
        f"Will check Flipkart registration status soon.\n\n"
        f"Use /start to go back to menu.",
        parse_mode="HTML"
    )
# ---------- Instagram Callbacks ----------
@bot.callback_query_handler(func=lambda call: call.data.startswith("instagram_"))
def handle_instagram_callback(call):
    action = call.data.split("_")[1]
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    msg_id = call.message.message_id
    balance, status = get_user_data(user_id)

    if action == "single":
        bot.answer_callback_query(call.id, "📹 Send a single Instagram video URL.")
        bot.edit_message_text(
            "📹 <b>Single Download</b>\n\n"
            "Send me the Instagram video link.\n"
            "Example: <code>https://www.instagram.com/reel/xyz123/</code>\n\n"
            "💡 I'll download and send the video to you.\n\n"
            "<i>Powered By Viediet Utility</i>",
            chat_id=chat_id,
            message_id=msg_id,
            reply_markup=instagram_menu_keyboard(),
            parse_mode="HTML"
        )

    elif action == "bulk":
        bot.answer_callback_query(call.id, "📚 Send multiple Instagram video URLs (one per line).")
        bot.edit_message_text(
            "📚 <b>Bulk Download</b>\n\n"
            "Send me multiple Instagram video links,\n"
            "each on a new line.\n\n"
            "Example:\n"
            "<code>https://www.instagram.com/reel/abc/\n"
            "https://www.instagram.com/reel/def/</code>\n\n"
            "💡 I'll download all and send them as a zip (coming soon).\n\n"
            "<i>Powered By Viediet Utility</i>",
            chat_id=chat_id,
            message_id=msg_id,
            reply_markup=instagram_menu_keyboard(),
            parse_mode="HTML"
        )
  # ---------- Instagram link handler (direct links) ----------
@bot.message_handler(func=lambda message: message.text and 'instagram.com' in message.text.lower())
def handle_instagram_link(message):
    bot.reply_to(
        message,
        "📥 <b>Instagram Downloader</b>\n\n"
        "Your request is being processed.\n"
        "This feature is under development.\n"
        "We'll download and send the video soon.\n\n"
        "⚠️ For now, only placeholder response.\n\n"
        "<i>Powered By Viediet Utility</i>",
        parse_mode="HTML"
    )      
# ---------- Back to Main ----------
@bot.callback_query_handler(func=lambda call: call.data == "back_menu")
def back_to_menu(call):
    user = call.from_user
    user_id = user.id
    balance, status = get_user_data(user_id)
    text = main_menu_text(user_id, user.first_name, balance, status)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, text, reply_markup=main_menu_keyboard(), parse_mode="HTML")
    bot.answer_callback_query(call.id)

# ---------- Fallback ----------
@bot.message_handler(func=lambda m: True)
def fallback(message):
    bot.reply_to(message, "❓ Unknown command. Use /start to see the menu.")

# ==================== MAIN ====================
if __name__ == "__main__":
    logger.info("🤖 Bot is starting...")
    try:
        bot.infinity_polling(timeout=30, long_polling_timeout=30)
    except Exception as e:
        logger.error(f"Polling error: {e}")
