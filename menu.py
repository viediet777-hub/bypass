# menu.py - Complete Menu Functions for Viediet Bot

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# ==================== MAIN MENU ====================
def main_menu_text(user_id, first_name, balance, status):
    return f"""
╔══════════════════════════════════╗
║     🚀 VIEDIET UTILITY BOT      ║
╚══════════════════════════════════╝

👋 Welcome back, <b>{first_name}</b>!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 <b>Balance:</b> <code>{balance}</code> Credits
👤 <b>User ID:</b> <code>{user_id}</code>
📊 <b>Status:</b> {status}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>⚡ Quick Actions:</b>
• Click <b>✨ Start Workflow</b> to access all modules
• Check <b>📊 Total Stats</b> for your usage
• Share <b>🔗 Bot Refer Link</b> to earn credits

<b>💡 Pro Tip:</b> Each module costs credits.
Earn free credits by referring friends!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<i>Made with ❤️ by @viedietextraa</i>
"""

def main_menu_keyboard(is_admin=False):
    kb = InlineKeyboardMarkup(row_width=2)
    
    # Main modules
    kb.row(
        InlineKeyboardButton("🔥 Firebase Extractor", callback_data="module_firebase"),
        InlineKeyboardButton("📧 Temp Mail", callback_data="module_temp")
    )
    kb.row(
        InlineKeyboardButton("🛒 Flipkart Checker", callback_data="module_flipkart"),
        InlineKeyboardButton("📸 Instagram Downloader", callback_data="module_instagram")
    )
    kb.row(
        InlineKeyboardButton("👁️ IG Viewer", callback_data="module_igviewer"),
        InlineKeyboardButton("🎵 Music Downloader", callback_data="module_music")
    )
    kb.row(
        InlineKeyboardButton("🛍️ Shopsy Mining", callback_data="module_shopsy"),
        InlineKeyboardButton("🧘 Yoga Referral", callback_data="module_yoga")
    )
    kb.row(
        InlineKeyboardButton("🔗 Referral System", callback_data="module_referral")
    )
    
    if is_admin:
        kb.row(InlineKeyboardButton("👑 Admin Panel", callback_data="module_admin"))
    
    return kb

# ==================== FIREBASE MENU ====================
def firebase_menu_text(user_id, balance, status, cost):
    return f"""
╔══════════════════════════════════╗
║     🔥 FIREBASE EXTRACTOR       ║
╚══════════════════════════════════╝

<b>📋 Module:</b> Firebase Extractor
<b>💰 Cost:</b> <code>{cost}</code> Credits
<b>💳 Balance:</b> <code>{balance}</code> Credits

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>📌 What it does:</b>
Extracts sensitive data from APK files:
• 🔥 Firebase URLs & Database endpoints
• 🔑 API Keys (Google, Firebase, etc.)
• 🔐 Secrets & Tokens
• 📦 Storage Buckets
• 📄 JSON Endpoints

<b>📤 How to use:</b>
1. Click <b>📤 Send APK</b>
2. Upload your APK file
3. Wait for analysis (30-60 sec)
4. Get extracted credentials

<b>⚠️ Warning:</b>
Only use on APKs you own!
"""

def firebase_menu_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.row(
        InlineKeyboardButton("📤 Send APK", callback_data="firebase_send"),
        InlineKeyboardButton("🗑️ Remove APK", callback_data="firebase_remove")
    )
    kb.row(InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu"))
    return kb

# ==================== TEMP MAIL MENU ====================
def temp_menu_text(user_id):
    return f"""
╔══════════════════════════════════╗
║      📧 TEMPORARY EMAIL         ║
╚══════════════════════════════════╝

<b>📋 Module:</b> Temp Mail Generator
<b>💰 Cost:</b> <code>FREE</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>📌 What it does:</b>
Creates disposable email addresses
• 📧 Receive emails instantly
• 🔑 Auto-detect OTP codes
• ⏱️ 10 minutes validity

<b>📤 How to use:</b>
1. Click <b>📧 New Email</b>
2. Copy your temp email
3. Use it for signups
4. Click <b>🔑 Get OTP</b> to auto-detect

<b>💡 Pro Tip:</b>
Perfect for OTP verification without sharing real email!
"""

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
    kb.row(InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu"))
    return kb

# ==================== FLIPKART MENU ====================
def flipkart_menu_text(user_id, balance, status, cost):
    return f"""
╔══════════════════════════════════╗
║     🛒 FLIPKART CHECKER         ║
╚══════════════════════════════════╝

<b>📋 Module:</b> Flipkart Number Checker
<b>💰 Cost:</b> <code>{cost}</code> Credits
<b>💳 Balance:</b> <code>{balance}</code> Credits

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>📌 What it does:</b>
Check if a phone number is registered on Flipkart
• 📱 Enter 10-digit number
• 🔍 Get registration status
• ⚡ Instant results

<b>📤 How to use:</b>
1. Click <b>📱 Check Number</b>
2. Enter 10-digit phone number
3. Get registration status

<b>📊 Status Results:</b>
✅ <b>VERIFIED</b> - Registered user
❌ <b>GUEST</b> - Not registered
⚠️ <b>API Blocked</b> - Try again later

<b>💡 Tip:</b> Use for lead generation!
"""

def flipkart_menu_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.row(InlineKeyboardButton("📱 Check Number", callback_data="flipkart_check"))
    kb.row(InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu"))
    return kb

# ==================== INSTAGRAM MENU ====================
def instagram_menu_text(user_id, balance, status, cost):
    return f"""
╔══════════════════════════════════╗
║     📸 INSTAGRAM DOWNLOADER     ║
╚══════════════════════════════════╝

<b>📋 Module:</b> Instagram Reel Downloader
<b>💰 Cost:</b> <code>{cost}</code> Credits per video
<b>💳 Balance:</b> <code>{balance}</code> Credits

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>📌 What it does:</b>
Download Instagram Reels & Videos
• 📹 Single reel download
• 📚 Bulk download (multiple reels)
• 🎬 High quality MP4

<b>📤 How to use:</b>
1. Click <b>📹 Single</b> or <b>📚 Bulk</b>
2. Send Instagram reel URL(s)
3. Get video(s) instantly

<b>📝 Examples:</b>
• Single: https://www.instagram.com/reel/xyz123/
• Bulk: one URL per line
"""

def instagram_menu_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.row(
        InlineKeyboardButton("📹 Single Download", callback_data="instagram_single"),
        InlineKeyboardButton("📚 Bulk Download", callback_data="instagram_bulk")
    )
    kb.row(InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu"))
    return kb

# ==================== REFERRAL MENU ====================
def referral_menu_text(user_id, balance, referral_count):
    return f"""
╔══════════════════════════════════╗
║      🔗 REFERRAL SYSTEM         ║
╚══════════════════════════════════╝

<b>📋 Module:</b> Referral Program
<b>💰 Balance:</b> <code>{balance}</code> Credits

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>📌 How it works:</b>
• Share your referral link
• Friends join via your link
• They stay 24 hours
• You earn <b>+{3} Credits</b>!

<b>📊 Your Stats:</b>
👥 <b>Referrals:</b> <code>{referral_count}</code>
⏳ <b>Pending:</b> <code>{get_pending_referral_count(user_id)}</code>
💰 <b>Bonus per referral:</b> <code>+3 Credits</code>

<b>🎁 Friend gets:</b> <b>+5 Credits</b> on joining!

<b>📤 How to use:</b>
1. Click <b>🔗 Get Link</b>
2. Share with friends
3. They join and stay
4. You earn credits!
"""

def referral_menu_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.row(
        InlineKeyboardButton("🔗 Get Link", callback_data="referral_get_link"),
        InlineKeyboardButton("📊 Stats", callback_data="referral_stats")
    )
    kb.row(InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu"))
    return kb

# ==================== ADMIN MENU ====================
def admin_panel_text():
    return f"""
╔══════════════════════════════════╗
║      👑 ADMIN PANEL            ║
╚══════════════════════════════════╝

<b>📋 Admin Controls</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>📊 Statistics:</b>
• Total Users
• Total Coins
• Usage Analytics

<b>👥 User Management:</b>
• View all users
• Add/Remove coins
• Ban/Unban users

<b>📢 Broadcasting:</b>
• Send messages to all users

<b>⚙️ Configuration:</b>
• Module costs
• Referral rewards
• System settings

<b>⚠️ Warning:</b>
Admin actions are irreversible!
Use with caution.
"""

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
        InlineKeyboardButton("⚙️ Costs", callback_data="admin_costs")
    )
    kb.row(InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu"))
    return kb

# ==================== MUSIC MENU ====================
def music_menu_text(user_id):
    return f"""
╔══════════════════════════════════╗
║      🎵 MUSIC DOWNLOADER        ║
╚══════════════════════════════════╝

<b>📋 Module:</b> Music Downloader
<b>💰 Cost:</b> <code>FREE</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>📌 What it does:</b>
Download high-quality MP3 songs
• 🎵 320kbps quality
• 🎤 Artist & album info
• 📥 Direct download

<b>📤 How to use:</b>
1. Send song or artist name
2. Select from search results
3. Download MP3 instantly

<b>🎶 Supported:</b>
• Hindi songs
• English songs
• Regional songs
• All genres

<b>💡 Tip:</b> Unlimited free downloads!
"""

def music_menu_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.row(InlineKeyboardButton("🎵 Search Song", callback_data="music_search"))
    kb.row(InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu"))
    return kb

# ==================== SHOPSY MENU ====================
def shopsy_menu_text(user_id, balance, status, shopsy_balance, is_logged_in):
    login_status = "✅ Logged In" if is_logged_in else "❌ Not Logged In"
    return f"""
╔══════════════════════════════════╗
║      🛍️ SHOPSY MINING          ║
╚══════════════════════════════════╝

<b>📋 Module:</b> Shopsy Auto-Mining
<b>💰 Cost:</b> <code>{get_module_cost('shopsy')}</code> Credits
<b>💳 Balance:</b> <code>{balance}</code> Credits

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>📌 What it does:</b>
Automatically play Shopsy games and earn coins
• 🎮 Auto-play games
• 🪙 Earn coins
• ⭐ Convert to points
• 📊 Track earnings

<b>📤 How to use:</b>
1. Click <b>🚀 Start Mining</b>
2. Enter 10-digit phone number
3. Enter OTP received
4. Auto-mine starts!

<b>📊 Your Stats:</b>
🪙 Shopsy Points: <code>{shopsy_balance}</code>
🔐 Status: {login_status}
⏱️ Mining: 1-2 minutes

<b>💡 Tip:</b> Higher coins = more points!
"""

def shopsy_menu_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.row(
        InlineKeyboardButton("🚀 Start Mining", callback_data="shopsy_start"),
        InlineKeyboardButton("📊 Stats", callback_data="shopsy_stats")
    )
    kb.row(
        InlineKeyboardButton("🚪 Logout", callback_data="shopsy_logout")
    )
    kb.row(InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu"))
    return kb

# ==================== YOGA MENU ====================
def yoga_menu_text(user_id, balance, status, yoga_code, reward, cost):
    code_display = f"`{yoga_code}`" if yoga_code else "❌ Not Set"
    return f"""
╔══════════════════════════════════╗
║      🧘 YOGA REFERRAL          ║
╚══════════════════════════════════╝

<b>📋 Module:</b> Yoga Referral Bot
<b>💰 Cost:</b> <code>{cost}</code> Credits
<b>🎁 Reward:</b> <code>+{reward}</code> Credits
<b>💳 Balance:</b> <code>{balance}</code> Credits

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>📌 What it does:</b>
Auto-register users on Habit.Yoga
• 📱 Phone number registration
• 🔐 OTP auto-verify
• 🎯 Earn referral rewards
• 📊 Track your referrals

<b>📤 How to use:</b>
1. Click <b>🧘 Start Referral</b>
2. Enter 10-digit phone number
3. Enter OTP received
4. Earn <b>+{reward} Credits</b>!

<b>📊 Your Yoga Code:</b>
{code_display}

<b>💡 Tip:</b> Set your code first!
Send link or code to setup.
"""

def yoga_menu_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.row(
        InlineKeyboardButton("🧘 Start Referral", callback_data="yoga_start"),
        InlineKeyboardButton("📊 Stats", callback_data="yoga_stats")
    )
    kb.row(
        InlineKeyboardButton("🔑 Set Code", callback_data="yoga_setcode")
    )
    kb.row(InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu"))
    return kb

# ==================== HELP MENU ====================
def help_menu_text():
    return """
╔══════════════════════════════════╗
║       💡 HELP & INFO           ║
╚══════════════════════════════════╝

<b>🤖 Bot Commands:</b>

<b>/start</b> - Show main menu
<b>/cancel</b> - Cancel current operation
<b>/addcoins</b> - Admin only
<b>/removecoins</b> - Admin only
<b>/broadcast</b> - Admin only
<b>/setcost</b> - Admin only

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>💰 Earning Credits:</b>
• 🎁 <b>+5</b> Welcome bonus
• 🔗 <b>+3</b> Per referral
• 🧘 <b>+4</b> Per Yoga referral
• 🛍️ Shopsy mining rewards

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>📱 Modules:</b>
• Firebase Extractor
• Temp Mail
• Flipkart Checker
• Instagram Downloader
• IG Viewer
• Music Downloader
• Shopsy Mining
• Yoga Referral

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<i>Made with ❤️ by @viedietextraa</i>
"""

# ==================== Helper Functions ====================
def get_pending_referral_count(user_id):
    """Helper function for referral menu"""
    import sqlite3
    conn = sqlite3.connect("viediet_bot.db", check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM pending_referrals WHERE referrer_id = ?', (user_id,))
    count = c.fetchone()[0]
    conn.close()
    return count

def get_module_cost(module):
    """Helper function for module costs"""
    import sqlite3
    conn = sqlite3.connect("viediet_bot.db", check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT value FROM config WHERE key = ?', (f"{module}_cost",))
    row = c.fetchone()
    conn.close()
    if row:
        return int(row[0])
    return 1  # Default cost
