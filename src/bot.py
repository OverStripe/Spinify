from telethon import TelegramClient, events
import os
import json
from src.approval_handler import handle_approve
from src.account_manager import handle_login
from src.group_manager import handle_add_group, handle_list_groups

# Load Configurations
with open("config/bot_config.json") as config_file:
    config = json.load(config_file)

# Bot Configurations
API_ID = config["api_id"]
API_HASH = config["api_hash"]
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = config["owner_id"]

# Initialize Telegram Client
bot = TelegramClient("SpinifyBot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    user = await event.get_sender()
    full_name = f"{user.first_name} {user.last_name or ''}".strip()

    message = (
        f"🌟 **Welcome to Spinify, {full_name}!**\n\n"
        "**About Spinify:**\n"
        "Spinify is your personal Telegram Ads Manager:\n"
        "- 🚀 Automate ad delivery.\n"
        "- 📋 Manage accounts and groups.\n"
        "- ⏱️ Schedule messages easily.\n\n"
        "**Commands:**\n"
        "1️⃣ /login - Authenticate your account.\n"
        "2️⃣ /add_group <group_username> - Add target groups.\n"
        "3️⃣ /list_groups - View your added groups.\n"
        "4️⃣ /set_ads_message <message> - Schedule ads.\n\n"
        "Use /login to get started!"
    )
    await event.reply(message)

# Register Handlers
bot.add_event_handler(handle_approve, events.NewMessage(pattern=r"/approve (\d+) (\d+)"))
bot.add_event_handler(handle_login, events.NewMessage(pattern="/login"))
bot.add_event_handler(handle_add_group, events.NewMessage(pattern=r"/add_group (.+)"))
bot.add_event_handler(handle_list_groups, events.NewMessage(pattern="/list_groups"))

def initialize_bot():
    print("🚀 Spinify Bot is running...")
    bot.run_until_disconnected()
