from telethon import TelegramClient, events
from src.account_manager import handle_login
from src.approval_handler import approve_user
import os

# Load configuration from environment variables or config file
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Make sure your .env file or environment variable has the token
API_ID = 22318470  # Replace with your actual API ID
API_HASH = "cf907c4c2d677b9f67d32828d891e97a"  # Replace with your actual API hash
OWNER_ID = os.getenv("OWNER_ID")  # Replace with the owner's Telegram ID

# Initialize Telegram Bot Client
bot = TelegramClient("SpinifyBot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    user = await event.get_sender()
    await event.reply(
        f"🌟 **Welcome to Spinify, {user.first_name}!**\n\n"
        "**Commands:**\n"
        "- `/login`: Log in to manage your account.\n"
        "- `/approve <user_id>`: Approve a user (owner only).\n\n"
        "Use `/login` to get started!"
    )

@bot.on(events.NewMessage(pattern="/login"))
async def handle_login_command(event):
    await handle_login(event)

@bot.on(events.NewMessage(pattern=r"/approve (\d+)"))
async def handle_approve(event):
    if str(event.sender_id) != str(OWNER_ID):
        await event.reply("❌ **Only the bot owner can use this command.**")
        return

    user_id = event.pattern_match.group(1)
    await approve_user(event, user_id)

# Start the bot
if __name__ == "__main__":
    print("🚀 Spinify Bot is running...")
    bot.run_until_disconnected()
