from telethon import TelegramClient, events
import asyncio
import json
import os

# Load config
with open("config/bot_config.json") as config_file:
    config = json.load(config_file)

# Bot configuration
API_ID = config["api_id"]
API_HASH = config["api_hash"]
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = config["owner_id"]

# Initialize bot client
bot = TelegramClient("SpinifyBot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.reply("Welcome to Spinify! 🌀 Use /login to get started.")

# Start the bot
print("Spinify bot is running...")
bot.run_until_disconnected()
