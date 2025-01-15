import os
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

APPROVED_USERS_DB = "data/approved_users.json"
SESSIONS_DIR = "data/sessions/"
API_ID = "your_api_id"
API_HASH = "your_api_hash"

def is_user_approved(user_id):
    with open(APPROVED_USERS_DB, "r") as file:
        approved_users = json.load(file)
        return str(user_id) in approved_users

def get_session_path(user_id):
    return os.path.join(SESSIONS_DIR, f"{user_id}.session")

async def handle_login(event):
    user_id = str(event.sender_id)
    if not is_user_approved(user_id):
        await event.reply("❌ You are not approved. Contact the admin.")
        return

    session_file = get_session_path(user_id)
    client = TelegramClient(session_file, API_ID, API_HASH)

    try:
        await client.connect()
        if not await client.is_user_authorized():
            await event.reply("📱 Enter your phone number (+1234567890):")
            phone_event = await event.client.wait_for_new_message(from_user=event.sender_id)
            phone_number = phone_event.message

            await client.send_code_request(phone_number)
            await event.reply("🔑 Enter the code sent to Telegram:")
            code_event = await event.client.wait_for_new_message(from_user=event.sender_id)
            code = code_event.message

            await client.sign_in(phone_number, code)
            await event.reply("✅ Login successful! Your session has been saved.")
    except SessionPasswordNeededError:
        await event.reply("🔐 2FA enabled. Enter your password:")
        password_event = await event.client.wait_for_new_message(from_user=event.sender_id)
        password = password_event.message
        await client.sign_in(password=password)
        await event.reply("✅ Login successful with 2FA!")
    except Exception as e:
        await event.reply(f"❌ Login failed: {e}")
    finally:
        await client.disconnect()
