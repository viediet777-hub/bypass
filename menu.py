# menu.py
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

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
    kb.add(InlineKeyboardButton("📱 Flipkart Checker", callback_data="module_flipkart", style="primary"))
    kb.add(InlineKeyboardButton("📥 Instagram Downloader", callback_data="module_instagram", style="primary"))  # NEW
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
def temp_menu_text(user_id: int) -> str:
    return (
        f"📧 <b>TEMP MAIL</b>\n\n"
        f"Click <b>New Email</b> to create a temporary email.\n"
        f"⏱️ Expires in 10 minutes.\n\n"
        f"<i>Powered By Viediet Utility</i>"
    )

def temp_menu_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.row(
        InlineKeyboardButton("📧 New Email", callback_data="temp_new", style="success"),
        InlineKeyboardButton("📥 Check Inbox", callback_data="temp_inbox", style="primary")
    )
    kb.row(
        InlineKeyboardButton("🔑 Get OTP", callback_data="temp_otp", style="primary"),
        InlineKeyboardButton("🗑️ Delete Email", callback_data="temp_delete", style="danger")
    )
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

# ========== INSTAGRAM DOWNLOADER SUB-MENU ==========
def instagram_menu_text(user_id: int, balance: int = 15, status: str = "ACTIVE") -> str:
    return (
        f"📥 <b>INSTAGRAM DOWNLOADER</b>\n\n"
        f"Status: <b>{status}</b>\n"
        f"Balance: <b>{balance} Credits</b>\n"
        f"Download Cost: <b>1 Credit / video</b>\n\n"
        f"Send Instagram video links (one per line for bulk).\n"
        f"Click <b>Single</b> to download one video, or <b>Bulk</b> for multiple.\n\n"
        f"💡 <b>How to use:</b>\n"
        f"1. Copy the Instagram video URL\n"
        f"2. Click Single or Bulk below\n"
        f"3. Paste your links\n\n"
        f"<i>Powered By Viediet Utility</i>"
    )

def instagram_menu_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.row(
        InlineKeyboardButton("📹 Single Download", callback_data="instagram_single", style="success"),
        InlineKeyboardButton("📚 Bulk Download", callback_data="instagram_bulk", style="primary")
    )
    kb.add(InlineKeyboardButton("🔙 Back to Main", callback_data="back_menu", style="danger"))
    return kb
