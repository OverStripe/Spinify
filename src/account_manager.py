import os
import json
import logging
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Constants
APPROVED_USERS_DB = "data/approved_users.json"
SESSIONS_DIR = "data/sessions/"
API_ID = 22318470  # Replace with your actual API_ID from bot_config.json
API_HASH = "cf907c4c2d677b9f67d32828d891e97a"  # Replace with your actual API_HASH from bot_config.json

# Ensure the sessions directory exists
if not os.path.exists(SESSIONS_DIR):
    os.makedirs(SESSIONS_DIR)

# Helper Functions
def is_user_approved(user_id):
    """Check if a user is approved to use the bot."""
    try:
        with open(APPROVED_USERS_DB, "r") as file:
            approved_users = json.load(file)
            return str(user_id) in approved_users
    except FileNotFoundError:
        logging.error("Approved users database not found.")
        return False

def get_session_path(user_id):
    """Get the session file path for a user."""
    return os.path.join(SESSIONS_DIR, f"{user_id}.session")

# Login Handler
async def handle_login(event):
    """Handle the /login command."""
    user_id = str(event.sender_id)
    logging.info("Login process started for user: %s", user_id)

    # Check if the user is approved
    if not is_user_approved(user_id):
        await event.reply("❌ **You are not approved to use this bot. Contact the admin.**")
        logging.warning("Unauthorized login attempt by user: %s", user_id)
        return

    # Initialize the Telegram client
    session_file = get_session_path(user_id)
    client = TelegramClient(session_file, API_ID, API_HASH)

    try:
        await client.connect()

        # If the user is not authorized, proceed with login flow
        if not await client.is_user_authorized():
            await event.reply("📱 **Please enter your phone number in the format:** `+1234567890`")
            phone_event = await event.client.wait_for_new_message(from_user=event.sender_id)
            phone_number = phone_event.message.strip()
            logging.info("Phone number received: %s", phone_number)

            # Send verification code
            await client.send_code_request(phone_number)
            await event.reply("🔑 **Enter the verification code sent to your Telegram:**")
            code_event = await event.client.wait_for_new_message(from_user=event.sender_id)
            verification_code = code_event.message.strip()
            logging.info("Verification code entered: %s", verification_code)

            # Sign in with the verification code
            await client.sign_in(phone_number, verification_code)
            await event.reply("✅ **Login successful! Your session has been saved.**")
            logging.info("Login successful for user: %s", user_id)
        else:
            await event.reply("✅ **You are already logged in.**")
            logging.info("User %s is already logged in.", user_id)
    except SessionPasswordNeededError:
        # Handle 2FA scenario
        await event.reply("🔐 **2FA enabled. Please enter your password:**")
        password_event = await event.client.wait_for_new_message(from_user=event.sender_id)
        password = password_event.message.strip()
        try:
            await client.sign_in(password=password)
            await event.reply("✅ **Login successful with 2FA! Your session has been saved.**")
            logging.info("Login with 2FA successful for user: %s", user_id)
        except Exception as e:
            await event.reply(f"❌ **Login failed with 2FA:** {e}")
            logging.error("2FA login failed for user %s: %s", user_id, e)
    except Exception as e:
        # General error handling
        await event.reply(f"❌ **Login failed:** {e}")
        logging.error("Login failed for user %s: %s", user_id, e)
    finally:
        await client.disconnect()
        logging.info("Client disconnected for user: %s", user_id)
