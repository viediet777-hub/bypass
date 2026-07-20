# menu.py
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ========== Helper function (matches main.py) ==========
def get_module_cost(module):
    """Get cost for a module - matches main.py function"""
    import sqlite3
    import os
    DB_PATH = "viediet_bot.db"
    
    # Default costs
    DEFAULT_COSTS = {
        "firebase": 2,
        "flipkart": 1,
        "instagram_single": 1,
        "instagram_bulk": 1,
        "crownit": 2,
        "shopsy": 1,
        "yoga": 1,
    }
    
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('SELECT value FROM config WHERE key = ?', (f"{module}_cost",))
        row = c.fetchone()
        conn.close()
        if row:
            return int(row[0])
        return DEFAULT_COSTS.get(module, 1)
    except:
        return DEFAULT_COSTS.get(module, 1)

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

def main_menu_keyboard(is_admin: bool = False):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("🔥 Firebase Extractor", callback_data="module_firebase", style="success"))
    kb.add(InlineKeyboardButton("📧 Temp Generator", callback_data="module_temp", style="primary"))
    kb.add(InlineKeyboardButton("📱 Flipkart Checker", callback_data="module_flipkart", style="primary"))
    kb.add(InlineKeyboardButton("📥 Instagram Downloader", callback_data="module_instagram", style="primary"))
    kb.add(InlineKeyboardButton("👁️ Instagram Viewer", callback_data="module_igviewer", style="primary"))
    kb.add(InlineKeyboardButton("🎵 Music", callback_data="module_music", style="primary"))
    kb.add(InlineKeyboardButton("⛏️ Shopsy Mining", callback_data="module_shopsy", style="primary"))
    kb.add(InlineKeyboardButton("🧘 Yoga Referral", callback_data="module_yoga", style="primary"))  # NEW
    kb.add(InlineKeyboardButton("🔗 Referral", callback_data="module_referral", style="primary"))
    if is_admin:
        kb.add(InlineKeyboardButton("👑 Admin Panel", callback_data="module_admin", style="danger"))
    return kb

# ========== FIREBASE ==========
def firebase_menu_text(user_id: int, balance: int = 15, status: str = "ACTIVE", cost: int = 2) -> str:
    return (
        f"🔥 <b>FIREBASE EXTRACTOR</b>\n\n"
        f"Status: <b>{status}</b>\n"
        f"Balance: <b>{balance} Credits</b>\n"
        f"Run Cost: <b>{cost} Credit(s) / scan</b>\n\n"
        f"Click <b>Send APK</b> to upload an APK file.\n"
        f"I'll extract:\n"
        f"• Firebase URLs\n"
        f"• API Keys\n"
        f"• Secrets & Tokens\n"
        f"• JSON Endpoints\n\n"
        f"⚠️ Analysis may take 30-60 seconds."
    )

def firebase_menu_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.row(
        InlineKeyboardButton("📤 Send APK", callback_data="firebase_send", style="primary"),
        InlineKeyboardButton("🗑️ Remove APK", callback_data="firebase_remove", style="danger")
    )
    kb.add(InlineKeyboardButton("🔙 Back to Main", callback_data="back_menu", style="danger"))
    return kb

# ========== TEMP MAIL ==========
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

# ========== FLIPKART ==========
def flipkart_menu_text(user_id: int, balance: int = 15, status: str = "ACTIVE", cost: int = 1) -> str:
    return (
        f"📱 <b>FLIPKART NUMBER CHECKER</b>\n\n"
        f"Status: <b>{status}</b>\n"
        f"Balance: <b>{balance} Credits</b>\n"
        f"Run Cost: <b>{cost} Credit(s) / check</b>\n\n"
        f"Send a phone number (10 digits) to check if it's registered on Flipkart/Shopsy."
    )

def flipkart_menu_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("🔙 Back to Main", callback_data="back_menu", style="danger"))
    return kb

# ========== INSTAGRAM ==========
def instagram_menu_text(user_id: int, balance: int = 15, status: str = "ACTIVE", cost: int = 1) -> str:
    return (
        f"📥 <b>INSTAGRAM DOWNLOADER</b>\n\n"
        f"Status: <b>{status}</b>\n"
        f"Balance: <b>{balance} Credits</b>\n"
        f"Download Cost: <b>{cost} Credit(s) / video</b>\n\n"
        f"Click <b>Single Download</b> for one reel, or <b>Bulk Download</b> for multiple.\n"
        f"Then send the Instagram video link(s)."
    )

def instagram_menu_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.row(
        InlineKeyboardButton("📹 Single Download", callback_data="instagram_single", style="success"),
        InlineKeyboardButton("📚 Bulk Download", callback_data="instagram_bulk", style="primary")
    )
    kb.add(InlineKeyboardButton("🔙 Back to Main", callback_data="back_menu", style="danger"))
    return kb

# ========== MUSIC (FREE) ==========
def music_menu_text(user_id: int, balance: int = 15, status: str = "ACTIVE", cost: int = 0) -> str:
    return (
        f"🎵 <b>MUSIC DOWNLOADER</b>\n\n"
        f"Status: <b>{status}</b>\n"
        f"Balance: <b>{balance} Credits</b>\n"
        f"Cost: <b>FREE</b> – unlimited downloads!\n\n"
        f"Send a song name or artist name to search and download."
    )

def music_menu_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("🔙 Back to Main", callback_data="back_menu", style="danger"))
    return kb

# ========== REFERRAL ==========
def referral_menu_text(user_id: int, balance: int = 15, referral_count: int = 0) -> str:
    return (
        f"🔗 <b>REFERRAL SYSTEM</b>\n\n"
        f"💰 Your Balance: <b>{balance} Credits</b>\n"
        f"👥 Total Referrals: <b>{referral_count}</b>\n\n"
        f"🎁 <b>How it works:</b>\n"
        f"• Share your referral link with friends\n"
        f"• Each friend gets <b>2 Credits</b> on joining\n"
        f"• You get <b>2 Credits</b> per referral\n"
        f"• Each feature use costs <b>1 Credit</b>\n\n"
        f"⚠️ <b>Rules:</b>\n"
        f"• Account must be 7+ days old\n"
        f"• Must stay in channel for 24 hours\n"
        f"• No self-referrals allowed\n"
        f"• One referral per user only\n\n"
        f"👇 Click below to get your referral link!"
    )

def referral_menu_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("🔗 Get Referral Link", callback_data="referral_get_link", style="success"))
    kb.add(InlineKeyboardButton("📊 My Referrals", callback_data="referral_stats", style="primary"))
    kb.add(InlineKeyboardButton("🔙 Back to Main", callback_data="back_menu", style="danger"))
    return kb

# ========== ADMIN ==========
def admin_panel_text() -> str:
    return (
        f"👑 <b>ADMIN PANEL</b>\n\n"
        f"Welcome, Admin!\n\n"
        f"Select an option below to manage the bot."
    )

def admin_panel_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.row(
        InlineKeyboardButton("📊 Stats", callback_data="admin_stats", style="primary"),
        InlineKeyboardButton("👥 Users", callback_data="admin_users", style="primary")
    )
    kb.row(
        InlineKeyboardButton("➕ Add Coins", callback_data="admin_add_coins", style="success"),
        InlineKeyboardButton("➖ Remove Coins", callback_data="admin_remove_coins", style="danger")
    )
    kb.row(
        InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast", style="primary"),
        InlineKeyboardButton("⚙️ Set Costs", callback_data="admin_costs", style="primary")
    )
    kb.add(InlineKeyboardButton("🔙 Back to Main", callback_data="back_menu", style="danger"))
    return kb

# ========== SHOPSY ==========
def shopsy_menu_text(user_id: int, balance: int = 15, status: str = "ACTIVE", shopsy_balance: int = 0, logged_in: int = 0) -> str:
    login_status = "✅ Logged in" if logged_in else "🔴 Not logged in"
    cost = get_module_cost("shopsy")
    return (
        f"⛏️ <b>SHOPSY MINING</b>\n\n"
        f"Status: <b>{status}</b>\n"
        f"Balance: <b>{balance} Credits</b>\n"
        f"💰 Shopsy Points: <b>{shopsy_balance}</b>\n"
        f"📱 Login: {login_status}\n"
        f"💡 Cost: <b>{cost} Credits</b> per run\n\n"
        f"Click <b>Start Mining</b> to begin.\n"
        f"• You'll enter your 10‑digit phone number\n"
        f"• OTP will be sent to your number\n"
        f"• I'll complete games and earn coins\n"
        f"• You get points based on coins earned!\n\n"
        f"⏱️ Process takes 1-2 minutes."
    )

def shopsy_menu_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.row(
        InlineKeyboardButton("⛏️ Start Mining", callback_data="shopsy_start", style="success"),
        InlineKeyboardButton("📊 My Stats", callback_data="shopsy_stats", style="primary")
    )
    kb.row(
        InlineKeyboardButton("🚪 Logout", callback_data="shopsy_logout", style="danger")
    )
    kb.add(InlineKeyboardButton("🔙 Back to Main", callback_data="back_menu", style="danger"))
    return kb

# ========== YOGA (NEW) ==========
def yoga_menu_text(user_id: int, balance: int = 15, status: str = "ACTIVE", yoga_code: str = None, reward: int = 4, cost: int = 1) -> str:
    code_status = f"✅ `{yoga_code}`" if yoga_code else "❌ Not set"
    return (
        f"🧘 <b>YOGA REFERRAL</b>\n\n"
        f"Status: <b>{status}</b>\n"
        f"Balance: <b>{balance} Credits</b>\n"
        f"Yoga Code: {code_status}\n"
        f"Cost: <b>{cost} Credit</b> per refer\n"
        f"Reward: <b>+{reward} Credits</b> per successful refer\n\n"
        f"🎯 <b>How it works:</b>\n"
        f"1. Set your Yoga code (if not set)\n"
        f"2. Enter phone number\n"
        f"3. Enter OTP\n"
        f"4. Earn points!\n\n"
        f"🌐 <b>Proxies:</b> Enabled for Yoga API"
    )

def yoga_menu_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.row(
        InlineKeyboardButton("🧘 Start Referral", callback_data="yoga_start", style="success"),
        InlineKeyboardButton("📊 My Stats", callback_data="yoga_stats", style="primary")
    )
    kb.row(
        InlineKeyboardButton("📝 Set Code", callback_data="yoga_setcode", style="primary")
    )
    kb.add(InlineKeyboardButton("🔙 Back to Main", callback_data="back_menu", style="danger"))
    return kb
