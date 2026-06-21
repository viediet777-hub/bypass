# menu.py
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random
import string

# ========== MAIN MENU ==========
def main_menu_text(user_id: int, username: str = None, balance: int = 15, status: str = "ACTIVE") -> str:
    return (
        f"🚀 <b>VIEDIET UTILITY BOT</b>\n\n"
        f"Hello, <b>{username or 'User'}</b>\n"
        f"Your workspace is ready.\n\n"
        f"╭─ ACCOUNT\n"
        f"├ 🆔 <code>{user_id}</code>\n"
        f"├ 💰 {balance} Credits\n"
        f"╰ ⭐ {status}\n\n"
        f"💎 Rewards, bypass tools, APK utilities and more — all available from the dashboard below.\n\n"
        f"👇 Choose a module to get started."
    )

def main_menu_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("🎁 Shopsy Coin", callback_data="module_shopsy", style="primary"))
    kb.add(InlineKeyboardButton("🔥 Firebase Extractor", callback_data="module_firebase", style="success"))
    kb.add(InlineKeyboardButton("📧 Temp Generator", callback_data="module_temp", style="primary"))
    kb.add(InlineKeyboardButton("📱 Flipkart Checker", callback_data="module_flipkart", style="primary"))   # NEW
    return kb

# ========== SHOPSY SUB-MENU ==========
def shopsy_menu_text(user_id: int, balance: int = 15, status: str = "ACTIVE") -> str:
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
        InlineKeyboardButton("▶️ Start New Task", callback_data="shopsy_start", style="success"),
        InlineKeyboardButton("📁 My Accounts", callback_data="shopsy_accounts", style="primary")
    )
    kb.add(InlineKeyboardButton("❓ How To Use", callback_data="shopsy_howto", style="primary"))
    kb.add(InlineKeyboardButton("🔙 Back to Main", callback_data="back_menu", style="danger"))
    return kb

# ========== FIREBASE EXTRACTOR SUB-MENU ==========
def firebase_menu_text(user_id: int, balance: int = 15, status: str = "ACTIVE") -> str:
    return (
        f"🔥 <b>FIREBASE EXTRACTOR</b>\n\n"
        f"Status: <b>{status}</b>\n"
        f"Balance: <b>{balance} Credits</b>\n"
        f"Run Cost: <b>2 Credits / scan</b>\n\n"
        f"Extract Firebase credentials from APK files.\n"
        f"Feature coming soon – placeholder for now."
    )

def firebase_menu_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("▶️ Start Scan", callback_data="firebase_start", style="success"))
    kb.add(InlineKeyboardButton("🔙 Back to Main", callback_data="back_menu", style="danger"))
    return kb

# ========== TEMP GENERATOR SUB-MENU ==========
def generate_temp_email():
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    domain = random.choice(["tempmail.com", "guerrillamail.com", "10minutemail.com", "temp-mail.org"])
    return f"{username}@{domain}"

def temp_menu_text(user_id: int, balance: int = 15, status: str = "ACTIVE") -> str:
    email = generate_temp_email()
    return (
        f"📧 <b>TEMP GENERATOR</b>\n\n"
        f"Your temporary email address:\n"
        f"<code>{email}</code>\n\n"
        f"Use this email to receive verification codes.\n"
        f"⚠️ Emails expire after 10 minutes.\n\n"
        f"Balance: <b>{balance} Credits</b>\n"
        f"Status: <b>{status}</b>"
    )

def temp_menu_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("🔄 Generate New Email", callback_data="temp_generate", style="success"))
    kb.add(InlineKeyboardButton("🔙 Back to Main", callback_data="back_menu", style="danger"))
    return kb

# ========== FLIPKART CHECKER SUB-MENU ==========
def flipkart_menu_text(user_id: int, balance: int = 15, status: str = "ACTIVE") -> str:
    return (
        f"📱 <b>FLIPKART NUMBER CHECKER</b>\n\n"
        f"Status: <b>{status}</b>\n"
        f"Balance: <b>{balance} Credits</b>\n"
        f"Run Cost: <b>1 Credit / check</b>\n\n"
        f"Send a phone number (10 digits) to check if it's registered on Flipkart/Shopsy."
    )

def flipkart_menu_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("🔙 Back to Main", callback_data="back_menu", style="danger"))
    return kb
