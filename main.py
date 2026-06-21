#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ==================== CONFIG ====================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    BOT_TOKEN = "7893651923:AAF2VrYFQMn3pjek06fti6eTlHFVkj7AUWI"  # fallback local
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

# ==================== VERSION CHECK ====================
print(f"🤖 pyTelegramBotAPI version: {telebot.__version__}")
if telebot.__version__ < "4.16.0":
    logger.warning("⚠️ Please upgrade pyTelegramBotAPI to >=4.16.0 for colored buttons.")

# ==================== BOT INIT ====================
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ==================== DATA STORE (in-memory) ====================
user_balances = {}
user_status = {}

def get_user_data(user_id):
    if user_id not in user_balances:
        user_balances[user_id] = 15
        user_status[user_id] = "ACTIVE"
    return user_balances[user_id], user_status[user_id]

# ==================== MAIN MENU ====================
def main_menu_text(user_id: int, username: str = None) -> str:
    balance, status = get_user_data(user_id)
    return (
        f"🚀 <b>VIEDIET UTILITY BOT</b>\n\n"
        f"Hello, <b>{username or 'User'}</b>\n"
        f"Your workspace is ready.\n\n"
        f"╭─ ACCOUNT\n"
        f"├ 🆔 <code>{user_id}</code>\n"
        f"├ 💰 {balance} Credits\n"
        f"╰ ⭐ {status}\n\n"
        f"💎 Rewards, bypass tools, APK utilities and more — all available from the dashboard below more featurs adding soon.\n\n"
        f"👇 Choose a module to get started."
    )

def main_menu_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    btn = InlineKeyboardButton(
        text="🎁 Shopsy Coin",
        callback_data="module_shopsy",
        style="primary"   # 🔵 blue
    )
    kb.add(btn)
    return kb

# ==================== SHOPSY SUB-MENU ====================
def shopsy_menu_text(user_id: int) -> str:
    balance, status = get_user_data(user_id)
    return (
        f"🎯 <b>SHOPSY AUTO-MINE</b>\n\n"
        f"Status: <b>{status}</b>\n"
        f"Balance: <b>{balance} Credits</b>\n"
        f"Run Cost: <b>1 Credit / run</b>\n\n"
        f"Select an operation below:"
    )

def shopsy_menu_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.row(
        InlineKeyboardButton("▶️ Start New Task", callback_data="shopsy_start", style="success"),  # 🟢 green
        InlineKeyboardButton("📁 My Accounts", callback_data="shopsy_accounts", style="primary")    # 🔵 blue
    )
    kb.add(
        InlineKeyboardButton("❓ How To Use", callback_data="shopsy_howto", style="primary")
    )
    kb.add(
        InlineKeyboardButton("🔙 Back to Main", callback_data="back_menu", style="danger")          # 🔴 red
    )
    return kb

# ==================== HANDLERS ====================

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user = message.from_user
    text = main_menu_text(user.id, user.first_name)
    bot.send_message(message.chat.id, text, reply_markup=main_menu_keyboard())

@bot.message_handler(commands=['ping'])
def ping_cmd(message):
    bot.reply_to(message, "🏓 Pong! Bot is alive.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("module_"))
def handle_module_callback(call):
    module = call.data.split("_")[1]
    if module == "shopsy":
        show_shopsy_menu(call)

def show_shopsy_menu(call):
    user_id = call.from_user.id
    bot.answer_callback_query(call.id)
    text = shopsy_menu_text(user_id)
    # Try to edit, if fails (e.g., colors not supported), send new message
    try:
        bot.edit_message_text(
            text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=shopsy_menu_keyboard(),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.warning(f"Edit failed: {e}. Sending new message.")
        # Delete old message and send new
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, text, reply_markup=shopsy_menu_keyboard(), parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data.startswith("shopsy_"))
def handle_shopsy_callback(call):
    action = call.data.split("_")[1]
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    msg_id = call.message.message_id

    if action == "start":
        balance, status = get_user_data(user_id)
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
        bot.edit_message_text(
            "✅ <b>Task Started!</b>\n\nYour Shopsy coin mining is now running.\n"
            f"Remaining Credits: {user_balances[user_id]}",
            chat_id=chat_id, message_id=msg_id,
            reply_markup=shopsy_menu_keyboard(),
            parse_mode="HTML"
        )
        # 🔜 Add actual Shopsy API call here later.

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

@bot.callback_query_handler(func=lambda call: call.data == "back_menu")
def back_to_menu(call):
    user = call.from_user
    text = main_menu_text(user.id, user.first_name)
    bot.edit_message_text(
        text,
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML"
    )
    bot.answer_callback_query(call.id)

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
