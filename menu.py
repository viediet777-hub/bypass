# ========== YOGA ==========
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
        f"🌐 Proxies: <b>Enabled</b> for Yoga API"
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
