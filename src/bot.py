from telethon import events
from src.approval_handler import approve_user

@bot.on(events.NewMessage(pattern=r"/approve (\d+) (\d+)"))
async def handle_approve(event):
    if str(event.sender_id) != str(OWNER_ID):
        await event.reply("❌ Only the owner can use this command.")
        return

    try:
        user_id, account_limit = event.pattern_match.groups()
        account_limit = int(account_limit)
        await approve_user(event, user_id, account_limit)
    except Exception as e:
        await event.reply(f"❌ Error processing /approve command: {e}")
