def start_shopsy_mining(user_id, chat_id):
    # ... (same as before)
    def mining_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(shopsy.mine_account_parallel(session_data, progress_callback, parallel_count=4))
        except Exception as e:
            result = {"status": "fail", "earned": 0, "msg": f"⚠️ Unexpected error: {str(e)[:100]}"}
        finally:
            loop.close()

        if result and result.get('status') == 'success':
            earned = result.get('earned', 0)
            final_coins = result.get('final_coins', 0)
            played = result.get('played', 0)
            total = result.get('total', 0)

            # ✅ Deduct credit ONLY on success
            update_user_balance(user_id, -1)

            update_shopsy_balance(user_id, earned)
            final_text = (
                f"✅ <b>Mining Complete!</b>\n\n"
                f"🎯 Earned: <b>{earned} SC</b>\n"
                f"💰 Total Shopsy Coins: <b>{final_coins} SC</b>\n"
                f"🎮 Games Played: {played}/{total}\n"
                f"📱 Phone: +91{phone}\n\n"
                f"💎 Your Shopsy Balance: {get_shopsy_balance(user_id)} SC"
            )
            bot.edit_message_text(final_text, chat_id, msg.message_id, parse_mode="HTML")
        else:
            err = result.get('msg', 'Unknown error') if result else 'Failed to mine.'
            bot.edit_message_text(f"❌ Mining failed!\n\n{err}", chat_id, msg.message_id)

        # Cleanup
        shopsy_temp_data.pop(user_id, None)
        user_shopsy_state.pop(user_id, None)
    # ... (rest)
