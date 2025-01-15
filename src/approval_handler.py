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

async def handle_approve(event):
    if str(event.sender_id) != str(OWNER_ID):
        await event.reply("❌ Only the owner can use this command.")
        return

    try:
        user_id, account_limit = event.pattern_match.groups()
        account_limit = int(account_limit)

        approved_users = load_approved_users()
        if user_id in approved_users:
            await event.reply(f"⚠️ User {user_id} is already approved.")
            return

        approved_users[user_id] = {"account_limit": account_limit, "used_accounts": 0}
        save_approved_users(approved_users)
        await event.reply(f"✅ User {user_id} approved with {account_limit} accounts.")
    except Exception as e:
        await event.reply(f"❌ Error: {e}")
