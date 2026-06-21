# menu.py
# All menu texts and keyboard layouts are defined here.

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
    # Future buttons:
    # kb.add(InlineKeyboardButton("🔥 Firebase Extractor", callback_data="module_firebase", style="success"))
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

# ========== FIREBASE EXTRACTOR (Future) ==========
def firebase_menu_text(user_id: int, balance: int = 15, status: str = "ACTIVE") -> str:
    return (
        f"🔥 <b>FIREBASE EXTRACTOR</b>\n\n"
        f"Status: <b>{status}</b>\n"
        f"Balance: <b>{balance} Credits</b>\n"
        f"Run Cost: <b>2 Credits / scan</b>\n\n"
        f"Send APK to extract Firebase credentials."
    )

def firebase_menu_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("▶️ Start Scan", callback_data="firebase_start", style="success"))
    kb.add(InlineKeyboardButton("🔙 Back to Main", callback_data="back_menu", style="danger"))
    return kb
