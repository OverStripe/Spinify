import json
import logging

# Constants
APPROVED_USERS_DB = "data/approved_users.json"

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def load_approved_users():
    """Load the approved users database."""
    try:
        with open(APPROVED_USERS_DB, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        logging.warning("Approved users database not found, creating a new one.")
        return {}

def save_approved_users(data):
    """Save the approved users database."""
    with open(APPROVED_USERS_DB, "w") as file:
        json.dump(data, file, indent=4)

async def approve_user(event, user_id):
    """Approve a new user dynamically."""
    # Ensure the user ID is numeric
    if not user_id.isdigit():
        await event.reply("❌ **Invalid user ID. Please provide a numeric user ID.**")
        logging.warning("Invalid user ID provided: %s", user_id)
        return

    # Load existing approved users
    approved_users = load_approved_users()

    if user_id in approved_users:
        await event.reply(f"⚠️ **User `{user_id}` is already approved.**")
        logging.info("User %s is already approved.", user_id)
        return

    # Add the new user
    approved_users[user_id] = {"account_limit": 1, "used_accounts": 0}  # Default limit is 1
    save_approved_users(approved_users)
    await event.reply(f"✅ **User `{user_id}` has been approved.**")
    logging.info("User %s approved successfully.", user_id)
