import os
import json
import logging
from telethon import TelegramClient

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

APPROVED_USERS_DB = "data/approved_users.json"
SESSIONS_DIR = "data/sessions/"
API_ID = 22318470  # Replace with your API ID
API_HASH = "cf907c4c2d677b9f67d32828d891e97a"  # Replace with your API hash

if not os.path.exists(SESSIONS_DIR):
    os.makedirs(SESSIONS_DIR)

def is_user_approved(user_id):
    try:
        with open(APPROVED_USERS_DB, "r") as file:
            approved_users = json.load(file)
            return str(user_id) in approved_users
    except FileNotFoundError:
        logging.error("Approved users database not found.")
        return False

def save_session_string(user_id, session_string):
    session_path = os.path.join(SESSIONS_DIR, f"{user_id}.session")
    with open(session_path, "w") as session_file:
        session_file.write(session_string)

async def handle_login(event):
    user_id = str(event.sender_id)
    if not is_user_approved(user_id):
        await event.reply("❌ **You are not approved to use this bot. Contact the admin.**")
        return

    await event.reply("🔑 **Please provide your session string to log in.**")
    session_event = await event.client.wait_for_new_message(from_user=event.sender_id)
    session_string = session_event.message.strip()

    try:
        save_session_string(user_id, session_string)
        client = TelegramClient(f"{SESSIONS_DIR}/{user_id}.session", API_ID, API_HASH)
        async with client:
            me = await client.get_me()
            await event.reply(f"✅ **Login successful! Welcome, {me.first_name}!**")
    except Exception as e:
        await event.reply(f"❌ **Login failed. Please check your session string:** {e}")
