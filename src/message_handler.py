import schedule
import asyncio
from telethon import TelegramClient
from src.group_manager import load_groups

SESSIONS_DIR = "data/sessions/"
API_ID = 22318470  # Replace with your actual API ID
API_HASH = "cf907c4c2d677b9f67d32828d891e97a"  # Replace with your actual API hash

async def send_ads_to_groups(user_id, message):
    """Send ad messages to all groups added by the user."""
    session_file = f"{SESSIONS_DIR}/{user_id}.session"
    client = TelegramClient(session_file, API_ID, API_HASH)

    try:
        await client.connect()
        if not await client.is_user_authorized():
            return "❌ **You are not logged in. Use /login to authenticate.**"

        groups = load_groups().get(str(user_id), [])
        if not groups:
            return "ℹ️ **No groups found. Add groups using /add_group.**"

        success_count = 0
        failed_groups = []

        for group in groups:
            try:
                await client.send_message(group, message)
                success_count += 1
            except Exception as e:
                failed_groups.append(group)

        await client.disconnect()

        result = f"✅ **Message sent to {success_count} groups.**"
        if failed_groups:
            result += f"\n❌ **Failed to send to: {', '.join(failed_groups)}**"
        return result
    except Exception as e:
        return f"❌ **Error sending ads:** {e}"

async def send_scheduled_ads(user_id, message):
    """Send scheduled ads to all groups."""
    session_file = f"{SESSIONS_DIR}/{user_id}.session"
    client = TelegramClient(session_file, API_ID, API_HASH)

    try:
        await client.connect()
        if not await client.is_user_authorized():
            return f"❌ **User {user_id} is not logged in.**"

        groups = load_groups().get(str(user_id), [])
        if not groups:
            return f"ℹ️ **No groups found for user {user_id}.**"

        for group in groups:
            try:
                await client.send_message(group, message)
            except Exception as e:
                print(f"❌ Failed to send to {group}: {e}")
    except Exception as e:
        print(f"❌ Error in scheduled ads for user {user_id}: {e}")
    finally:
        await client.disconnect()

def schedule_ads(user_id, message, interval_hours):
    """Schedule ads for a user."""
    schedule.every(interval_hours).hours.do(
        asyncio.run, send_scheduled_ads(user_id, message)
    )
    return f"✅ **Scheduled ads every {interval_hours} hour(s).**"
