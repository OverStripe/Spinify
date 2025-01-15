import json
from telethon import events

APPROVED_USERS_DB = "data/approved_users.json"

# Load approved users
def load_approved_users():
    try:
        with open(APPROVED_USERS_DB, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Save approved users
def save_approved_users(data):
    with open(APPROVED_USERS_DB, "w") as file:
        json.dump(data, file, indent=4)

# Approve a user
async def approve_user(event, user_id, account_limit):
    approved_users = load_approved_users()

    if user_id in approved_users:
        await event.reply(f"⚠️ User {user_id} is already approved with {approved_users[user_id]['account_limit']} accounts.")
        return

    approved_users[user_id] = {"account_limit": account_limit, "used_accounts": 0}
    save_approved_users(approved_users)

    await event.reply(f"✅ User {user_id} has been approved with a limit of {account_limit} accounts.")
  
