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
    kb.add(InlineKeyboardButton("🔥 Firebase Extractor", callback_data="module_firebase", style="success"))
    kb.add(InlineKeyboardButton("📧 Temp Generator", callback_data="module_temp", style="primary"))
    kb.add(InlineKeyboardButton("📱 Flipkart Checker", callback_data="module_flipkart", style="primary"))
    kb.add(InlineKeyboardButton("📥 Instagram Downloader", callback_data="module_instagram", style="primary"))
    kb.add(InlineKeyboardButton("🔐 Session Extractor", callback_data="module_session", style="primary"))
    kb.add(InlineKeyboardButton("🏨 Brevistay", callback_data="module_brevistay", style="primary"))
    kb.add(InlineKeyboardButton("🧘 Yoga", callback_data="module_habuild", style="primary"))
    kb.add(InlineKeyboardButton("🎵 Music", callback_data="module_music", style="primary"))
    kb.add(InlineKeyboardButton("🔗 Referral", callback_data="module_referral", style="primary"))
    if is_admin:
        kb.add(InlineKeyboardButton("👑 Admin Panel", callback_data="module_admin", style="danger"))
    return kb

# ========== HABUILD SUB-MENU ==========
def habuild_menu_text(user_id: int, balance: int = 15, status: str = "ACTIVE", cost: int = 1) -> str:
    return (
        f"🧘 <b>HABUILD REFERRAL AUTOMATION</b>\n\n"
        f"Status: <b>{status}</b>\n"
        f"Balance: <b>{balance} Credits</b>\n"
        f"Run Cost: <b>{cost} Credit(s) / referral</b>\n\n"
        f"Click <b>Start Automation</b> to begin.\n"
        f"Bot will:\n"
        f"• Fetch numbers from your Firebase panel\n"
        f"• Auto-register with your referral code\n"
        f"• Auto-detect and verify OTP\n"
        f"• Complete referral automatically\n\n"
        f"⚙️ <b>Setup:</b>\n"
        f"1. Set your Habuild referral code\n"
        f"2. Add your Firebase panel URL\n"
        f"3. Start automation\n\n"
        f"⚠️ Make sure your panel has active devices!"
    )

def habuild_menu_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("▶️ Start Automation", callback_data="habuild_start", style="success"))
    kb.add(InlineKeyboardButton("⏹️ Stop Automation", callback_data="habuild_stop", style="danger"))
    kb.add(InlineKeyboardButton("📊 My Stats", callback_data="habuild_stats", style="primary"))
    kb.add(InlineKeyboardButton("⚙️ Set Referral Code", callback_data="habuild_set_ref", style="primary"))
    kb.add(InlineKeyboardButton("📁 Add Panel", callback_data="habuild_add_panel", style="primary"))
    kb.add(InlineKeyboardButton("🔙 Back to Main", callback_data="back_menu", style="danger"))
    return kb

# ========== BREVISTAY SUB-MENU ==========
def brevistay_menu_text(user_id: int, balance: int = 15, status: str = "ACTIVE", cost: int = 1) -> str:
    return (
        f"🏨 <b>BREVISTAY REFERRAL AUTOMATION</b>\n\n"
        f"Status: <b>{status}</b>\n"
        f"Balance: <b>{balance} Credits</b>\n"
        f"Run Cost: <b>{cost} Credit(s) / referral</b>\n\n"
        f"Click <b>Start Referral</b> to begin.\n"
        f"Bot will:\n"
        f"• Generate random Indian name & email\n"
        f"• Send OTP to your phone\n"
        f"• Complete registration with your referral code\n"
        f"• Verify email automatically\n\n"
        f"⚠️ Make sure you have a Brevistay account!"
    )

def brevistay_menu_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("▶️ Start Referral", callback_data="brevistay_start", style="success"))
    kb.add(InlineKeyboardButton("❓ How To Use", callback_data="brevistay_howto", style="primary"))
    kb.add(InlineKeyboardButton("🔙 Back to Main", callback_data="back_menu", style="danger"))
    return kb

# ========== SHOPSY SUB-MENU ==========
def shopsy_menu_text(user_id: int, balance: int = 15, status: str = "ACTIVE", cost: int = 1) -> str:
    return (
        f"🎯 <b>SHOPSY AUTO-MINE</b>\n\n"
        f"Status: <b>{status}</b>\n"
        f"Balance: <b>{balance} Credits</b>\n"
        f"Run Cost: <b>{cost} Credit(s) / run</b>\n\n"
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

# ========== INSTAGRAM DOWNLOADER SUB-MENU ==========
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

# ========== SESSION EXTRACTOR SUB-MENU ==========
def session_menu_text(user_id: int, balance: int = 15, status: str = "ACTIVE", cost: int = 1) -> str:
    return (
        f"🔐 <b>SESSION EXTRACTOR</b>\n\n"
        f"Status: <b>{status}</b>\n"
        f"Balance: <b>{balance} Credits</b>\n"
        f"Run Cost: <b>{cost} Credit(s) / session</b>\n\n"
        f"Click <b>Start</b> to extract your Flipkart/Shopsy session.\n"
        f"Send your 10-digit phone number, verify OTP, and get full session JSON."
    )

def session_menu_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("🔐 Start Extraction", callback_data="session_flipkart", style="success"))
    kb.add(InlineKeyboardButton("🔙 Back to Main", callback_data="back_menu", style="danger"))
    return kb

# ========== MUSIC SUB-MENU ==========
def music_menu_text(user_id: int, balance: int = 15, status: str = "ACTIVE", cost: int = 1) -> str:
    return (
        f"🎵 <b>MUSIC DOWNLOADER</b>\n\n"
        f"Status: <b>{status}</b>\n"
        f"Balance: <b>{balance} Credits</b>\n"
        f"Cost: <b>{cost} Credit(s) / song</b>\n\n"
        f"Send a song name or artist name to search and download."
    )

def music_menu_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("🔙 Back to Main", callback_data="back_menu", style="danger"))
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
    kb.add(InlineKeyboardButton("🔗 Get Referral Link", callback_data="referral_get_link", style="success"))
    kb.add(InlineKeyboardButton("📊 My Referrals", callback_data="referral_stats", style="primary"))
    kb.add(InlineKeyboardButton("🔙 Back to Main", callback_data="back_menu", style="danger"))
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
