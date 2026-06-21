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
    kb.add(InlineKeyboardButton("🎁 Shopsy Coin", callback_data="module_shopsy", style="primary"))
    kb.add(InlineKeyboardButton("🔥 Firebase Extractor", callback_data="module_firebase", style="success"))
    kb.add(InlineKeyboardButton("📧 Temp Generator", callback_data="module_temp", style="primary"))
    kb.add(InlineKeyboardButton("📱 Flipkart Checker", callback_data="module_flipkart", style="primary"))
    kb.add(InlineKeyboardButton("📥 Instagram Downloader", callback_data="module_instagram", style="primary"))
    kb.add(InlineKeyboardButton("🔗 Referral", callback_data="module_referral", style="primary"))   # NEW
    if is_admin:
        kb.add(InlineKeyboardButton("👑 Admin Panel", callback_data="module_admin", style="danger"))
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

# ========== OTHER SUB-MENUS (unchanged) ==========
# ... (keep all other menu functions as they are) ...
