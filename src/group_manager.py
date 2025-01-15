import json

GROUPS_DB = "data/groups.json"

# Load groups data
def load_groups():
    try:
        with open(GROUPS_DB, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Save groups data
def save_groups(data):
    with open(GROUPS_DB, "w") as file:
        json.dump(data, file, indent=4)

# Add a group
async def add_group(event, user_id, group_username):
    groups = load_groups()

    # Ensure user has an entry
    if str(user_id) not in groups:
        groups[str(user_id)] = []

    # Add the group if not already in the list
    if group_username not in groups[str(user_id)]:
        groups[str(user_id)].append(group_username)
        save_groups(groups)
        await event.reply(f"✅ Group '{group_username}' has been added successfully.")
    else:
        await event.reply(f"⚠️ Group '{group_username}' is already in your list.")
      
