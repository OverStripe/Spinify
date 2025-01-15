from telethon import TelegramClient, events
import os
import json
from src.approval_handler import handle_approve
from src.account_manager import handle_login
from src.group_manager import handle_add_group, handle_list_groups

# Load config
with open("config/bot_config.json") as config_file:
    config = json.load(config_file)

# Bot configuration
API_ID = config["api_id"]
API_HASH = config["api_hash"]
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = config["owner_id"]

# Initialize bot
bot = TelegramClient("SpinifyBot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.reply("Welcome to Spinify! 🌀 Use /login to get started.")

# Register handlers
bot.add_event_handler(handle_approve, events.NewMessage(pattern=r"/approve (\d+) (\d+)"))
bot.add_event_handler(handle_login, events.NewMessage(pattern="/login"))
bot.add_event_handler(handle_add_group, events.NewMessage(pattern=r"/add_group (.+)"))
bot.add_event_handler(handle_list_groups, events.NewMessage(pattern="/list_groups"))

# Start the bot
print("Spinify bot is running...")
bot.run_until_disconnected()
