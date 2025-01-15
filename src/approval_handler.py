import json

APPROVED_USERS_DB = "data/approved_users.json"

def load_approved_users():
    try:
        with open(APPROVED_USERS_DB, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_approved_users(data):
    with open(APPROVED_USERS_DB, "w") as file:
        json.dump(data, file, indent=4)

async def approve_user(event, user_id):
    if not user_id.isdigit():
        await event.reply("❌ **Invalid user ID. Please provide a numeric user ID.**")
        return

    approved_users = load_approved_users()
    if user_id in approved_users:
        await event.reply(f"⚠️ **User `{user_id}` is already approved.**")
        return

    approved_users[user_id] = {"account_limit": 1, "used_accounts": 0}
    save_approved_users(approved_users)
    await event.reply(f"✅ **User `{user_id}` has been approved.**")
