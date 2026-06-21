#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ==================== CONFIG ====================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7893651923:AAF2VrYFQMn3pjek06fti6eTlHFVkj7AUWI")  # Railway env

# ==================== LOGGING ====================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== BOT INIT ====================
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ==================== MAIN MENU ====================
def main_menu(user_id: int, username: str = None) -> str:
    balance = 15
    status = "FREE USER"
    user_id_display = user_id
    user_name_display = username or "User"

    return (
        f"🚀 <b>VIEDIET UTILITY BOT</b>\n\n"
        f"Hello, <b>{user_name_display}</b>\n"
        f"Your workspace is ready.\n\n"
        f"╭─ ACCOUNT\n"
        f"├ 🆔 <code>{user_id_display}</code>\n"
        f"├ 💰 {balance} Credits\n"
        f"╰ ⭐ {status}\n\n"
        f"💎 Rewards, bypass tools, APK utilities and more — all available from the dashboard below more featurs adding soon.\n\n"
        f"👇 Choose a module to get started."
    )

def main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    btn_shopsy = InlineKeyboardButton("🎁 Shopsy Coin", callback_data="module_shopsy")
    keyboard.add(btn_shopsy)
    return keyboard

# ==================== HANDLERS ====================

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user = message.from_user
    text = main_menu(user.id, user.first_name)
    keyboard = main_menu_keyboard()
    bot.send_message(message.chat.id, text, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith("module_"))
def handle_module_callback(call):
    module = call.data.split("_")[1]
    if module == "shopsy":
        bot.answer_callback_query(call.id, "⏳ Module loading...")
        bot.edit_message_text(
            "🎁 <b>Shopsy Coin Module</b>\n\n"
            "Send your phone number to start:\n"
            "Example: <code>9876543210</code>",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="HTML"
        )
        back_btn = InlineKeyboardMarkup().add(
            InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu")
        )
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=back_btn)
    # add more modules here

@bot.callback_query_handler(func=lambda call: call.data == "back_menu")
def back_to_menu(call):
    user = call.from_user
    text = main_menu(user.id, user.first_name)
    keyboard = main_menu_keyboard()
    bot.edit_message_text(
        text,
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    bot.answer_callback_query(call.id)

# ==================== FALLBACK ====================
@bot.message_handler(func=lambda m: True)
def fallback(message):
    bot.reply_to(message, "❓ Unknown command. Use /start to see the menu.")

# ==================== MAIN ====================
if __name__ == "__main__":
    logger.info("🤖 VIEDIET BYPASS MENU BOT starting...")
    bot.infinity_polling(timeout=30, long_polling_timeout=30)
