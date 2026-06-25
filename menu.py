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

def main_menu_keyboard(is_admin: bool = False):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("🔥 Firebase Extractor", callback_data="module_firebase"))
    kb.add(InlineKeyboardButton("📧 Temp Generator", callback_data="module_temp"))
    kb.add(InlineKeyboardButton("📱 Flipkart Checker", callback_data="module_flipkart"))
    kb.add(InlineKeyboardButton("📥 Instagram Downloader", callback_data="module_instagram"))
    kb.add(InlineKeyboardButton("🔐 Session Extractors", callback_data="module_session"))   # NEW
    kb.add(InlineKeyboardButton("🎵 Music", callback_data="module_music"))
    kb.add(InlineKeyboardButton("🔗 Referral", callback_data="module_referral"))
    if is_admin:
        kb.add(InlineKeyboardButton("👑 Admin Panel", callback_data="module_admin"))
    return kb

# ========== FIREBASE EXTRACTOR SUB-MENU ==========
def firebase_menu_text(user_id: int, balance: int = 15, status: str = "ACTIVE") -> str:
    return (
        f"🔥 <b>FIREBASE EXTRACTOR</b>\n\n"
        f"Status: <b>{status}</b>\n"
        f"Balance: <b>{balance} Credits</b>\n"
        f"Run Cost: <b>2 Credits / scan</b>\n\n"
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
        InlineKeyboardButton("📤 Send APK", callback_data="firebase_send"),
        InlineKeyboardButton("🗑️ Remove APK", callback_data="firebase_remove")
    )
    kb.add(InlineKeyboardButton("🔙 Back to Main", callback_data="back_menu"))
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
        InlineKeyboardButton("📧 New Email", callback_data="temp_new"),
        InlineKeyboardButton("📥 Check Inbox", callback_data="temp_inbox")
    )
    kb.row(
        InlineKeyboardButton("🔑 Get OTP", callback_data="temp_otp"),
        InlineKeyboardButton("🗑️ Delete Email", callback_data="temp_delete")
    )
    kb.add(InlineKeyboardButton("🔙 Back to Main", callback_data="back_menu"))
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
    kb.add(InlineKeyboardButton("🔙 Back to Main", callback_data="back_menu"))
    return kb

# ========== INSTAGRAM DOWNLOADER SUB-MENU ==========
def instagram_menu_text(user_id: int, balance: int = 15, status: str = "ACTIVE") -> str:
    return (
        f"📥 <b>INSTAGRAM DOWNLOADER</b>\n\n"
        f"Status: <b>{status}</b>\n"
        f"Balance: <b>{balance} Credits</b>\n"
        f"Download Cost: <b>1 Credit / video</b>\n\n"
        f"Click <b>Single Download</b> for one reel, or <b>Bulk Download</b> for multiple.\n"
        f"Then send the Instagram video link(s)."
    )

def instagram_menu_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.row(
        InlineKeyboardButton("📹 Single Download", callback_data="instagram_single"),
        InlineKeyboardButton("📚 Bulk Download", callback_data="instagram_bulk")
    )
    kb.add(InlineKeyboardButton("🔙 Back to Main", callback_data="back_menu"))
    return kb

# ========== REFERRAL SUB-MENU ==========
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
        f"• Must stay in channel/group for 24 hours\n"
        f"• No self-referrals allowed\n"
        f"• One referral per user only\n\n"
        f"👇 Click below to get your referral link!"
    )

def referral_menu_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("🔗 Get Referral Link", callback_data="referral_get_link"))
    kb.add(InlineKeyboardButton("📊 My Referrals", callback_data="referral_stats"))
    kb.add(InlineKeyboardButton("🔙 Back to Main", callback_data="back_menu"))
    return kb

# ========== ADMIN PANEL SUB-MENU ==========
def admin_panel_text() -> str:
    return (
        f"👑 <b>ADMIN PANEL</b>\n\n"
        f"Welcome, Admin!\n\n"
        f"Select an option below to manage the bot."
    )

def admin_panel_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.row(
        InlineKeyboardButton("📊 Stats", callback_data="admin_stats"),
        InlineKeyboardButton("👥 Users", callback_data="admin_users")
    )
    kb.row(
        InlineKeyboardButton("➕ Add Coins", callback_data="admin_add_coins"),
        InlineKeyboardButton("➖ Remove Coins", callback_data="admin_remove_coins")
    )
    kb.row(
        InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
        InlineKeyboardButton("⚙️ Set Costs", callback_data="admin_costs")
    )
    kb.add(InlineKeyboardButton("🔙 Back to Main", callback_data="back_menu"))
    return kb

# ========== SESSION EXTRACTOR SUB-MENU ==========
def session_menu_text(user_id: int, balance: int = 15, status: str = "ACTIVE") -> str:
    return (
        f"🔐 <b>SESSION EXTRACTORS</b>\n\n"
        f"Balance: <b>{balance} Credits</b>\n"
        f"Cost: <b>1 Credit / extraction</b>\n\n"
        f"Choose a service to extract your session JSON:\n\n"
        f"📱 <b>Flipkart/Shopsy</b> – full session tokens\n"
        f"🛵 <b>Swiggy</b> – coming soon\n"
        f"🛒 <b>Blinkit</b> – coming soon\n\n"
        f"<i>Session data is saved as a JSON file.</i>"
    )

def session_menu_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.row(
        InlineKeyboardButton("📱 Flipkart/Shopsy", callback_data="session_flipkart"),
        InlineKeyboardButton("🛵 Swiggy", callback_data="session_swiggy")
    )
    kb.row(
        InlineKeyboardButton("🛒 Blinkit", callback_data="session_blinkit"),
        InlineKeyboardButton("🔙 Back", callback_data="back_menu")
    )
    return kb
