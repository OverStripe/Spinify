import json

GROUPS_DB = "data/groups.json"

def load_groups():
    try:
        with open(GROUPS_DB, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_groups(data):
    with open(GROUPS_DB, "w") as file:
        json.dump(data, file, indent=4)

async def handle_add_group(event, user_id, group_username):
    groups = load_groups()
    if user_id not in groups:
        groups[user_id] = []

    if group_username not in groups[user_id]:
        groups[user_id].append(group_username)
        save_groups(groups)
        await event.reply(f"✅ **Group `{group_username}` has been added successfully.**")
    else:
        await event.reply(f"⚠️ **Group `{group_username}` is already in your list.**")

async def handle_list_groups(event, user_id):
    groups = load_groups().get(user_id, [])
    if groups:
        group_list = "\n".join([f"- `{group}`" for group in groups])
        await event.reply(f"📋 **Your Groups:**\n{group_list}")
    else:
        await event.reply("ℹ️ **You haven't added any groups yet.**")
