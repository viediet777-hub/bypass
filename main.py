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
from datetime import datetime, timedelta
from menu import (
    main_menu_text, main_menu_keyboard,
    shopsy_menu_text, shopsy_menu_keyboard,
    firebase_menu_text, firebase_menu_keyboard,
    temp_menu_text, temp_menu_keyboard,
    flipkart_menu_text, flipkart_menu_keyboard,
    instagram_menu_text, instagram_menu_keyboard
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
user_instagram_state = {}  # user_id -> "single" or "bulk"

def get_user_data(user_id):
    if user_id not in user_balances:
        user_balances[user_id] = 15
        user_status[user_id] = "ACTIVE"
    return user_balances[user_id], user_status[user_id]

# ==================== TEMP MAIL CLASS ====================
class TempMailBot:
    # ... (keep exactly as before) ...
    pass

# ==================== FLIPKART CHECKER ====================
def check_flipkart(num):
    """Check Flipkart registration status – from provided script"""
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
            return f"⚠️ Number not found in response. Raw: {jsonData}"
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
        filename = f"{shortcode}.mp4"
        L.download_post(post, target=shortcode)
        for file in os.listdir(shortcode):
            if file.endswith(".mp4"):
                return os.path.join(shortcode, file)
        return None
    except Exception as e:
        logger.error(f"Insta download error: {e}")
        return None

def download_bulk(urls):
    """Download multiple reels and return list of file paths"""
    results = []
    for url in urls:
        path = download_reel(url)
        if path:
            results.append(path)
        time.sleep(1)  # avoid rate limit
    return results

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
# ... (keep existing temp callbacks unchanged) ...

# ---------- Flipkart Callbacks ----------
@bot.callback_query_handler(func=lambda call: call.data.startswith("flipkart_"))
def handle_flipkart_callback(call):
    # User clicked something in flipkart menu – we just let them send a number directly.
    # We'll handle number in the phone handler.
    bot.answer_callback_query(call.id, "📱 Send a 10-digit number to check.")

@bot.message_handler(func=lambda message: message.text and message.text.isdigit() and len(message.text) == 10)
def handle_phone_number(message):
    user_id = message.from_user.id
    balance, status = get_user_data(user_id)
    # Check if user has enough credits (cost 1)
    if balance < 1:
        bot.reply_to(message, "❌ Insufficient credits! You need 1 credit to check a number.")
        return
    # Deduct credit
    user_balances[user_id] = balance - 1
    # Send processing message
    processing = bot.reply_to(message, f"🔍 Checking <code>{message.text}</code> on Flipkart...", parse_mode="HTML")
    # Run check in thread to avoid blocking
    def check_thread():
        result = check_flipkart(message.text)
        new_balance, _ = get_user_data(user_id)
        bot.edit_message_text(
            f"📱 <b>Result for {message.text}</b>\n\n{result}\n\n💰 Remaining Credits: {new_balance}",
            chat_id=message.chat.id,
            message_id=processing.message_id,
            parse_mode="HTML"
        )
    threading.Thread(target=check_thread).start()

# ---------- Instagram Callbacks ----------
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

# Instagram link handler (direct links)
@bot.message_handler(func=lambda message: message.text and 'instagram.com' in message.text.lower())
def handle_instagram_link(message):
    user_id = message.from_user.id
    balance, status = get_user_data(user_id)
    state = user_instagram_state.get(user_id)

    if not state:
        # If user didn't click a button, tell them to use the menu
        bot.reply_to(message, "📥 Please use the Instagram Downloader module from the main menu to send links.")
        return

    # Parse links
    lines = message.text.strip().splitlines()
    urls = [line.strip() for line in lines if 'instagram.com' in line]

    if not urls:
        bot.reply_to(message, "❌ No valid Instagram URLs found.")
        return

    if state == "single":
        if balance < 1:
            bot.reply_to(message, "❌ Insufficient credits! You need 1 credit to download.")
            return
        # Process single
        user_balances[user_id] = balance - 1
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
        user_balances[user_id] = balance - total_cost
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

    # Reset state after processing
    user_instagram_state[user_id] = None

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
