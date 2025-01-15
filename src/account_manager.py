import os
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

APPROVED_USERS_DB = "data/approved_users.json"
SESSIONS_DIR = "data/sessions/"
API_ID = "your_api_id"
API_HASH = "your_api_hash"

def is_user_approved(user_id):
    try:
        with open(APPROVED_USERS_DB, "r") as file:
            approved_users = json.load(file)
            return str(user_id) in approved_users
    except FileNotFoundError:
        return False

def get_session_path(user_id):
    return os.path.join(SESSIONS_DIR, f"{user_id}.session")

async def handle_login(event):
    user_id = str(event.sender_id)
    if not is_user_approved(user_id):
        await event.reply("❌ **You are not approved. Contact the admin to request access.**")
        return

    session_file = get_session_path(user_id)
    client = TelegramClient(session_file, API_ID, API_HASH)

    try:
        await client.connect()
        if not await client.is_user_authorized():
            await event.reply("📱 **Enter your phone number in the format:** `+1234567890`")
            phone_event = await event.client.wait_for_new_message(from_user=event.sender_id)
            phone_number = phone_event.message.strip()

            await client.send_code_request(phone_number)
            await event.reply("🔑 **Enter the verification code sent to your Telegram:**")
            code_event = await event.client.wait_for_new_message(from_user=event.sender_id)
            code = code_event.message.strip()

            await client.sign_in(phone_number, code)
            await event.reply("✅ **Login successful! Your session has been saved.**")
    except SessionPasswordNeededError:
        await event.reply("🔐 **2FA enabled. Please enter your password:**")
        password_event = await event.client.wait_for_new_message(from_user=event.sender_id)
        password = password_event.message.strip()
        await client.sign_in(password=password)
        await event.reply("✅ **Login successful with 2FA!**")
    except Exception as e:
        await event.reply(f"❌ **Login failed:** {e}")
    finally:
        await client.disconnect()
