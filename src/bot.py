from telethon import TelegramClient, events
from src.account_manager import handle_login
from src.approval_handler import approve_user
from src.group_manager import handle_add_group, handle_list_groups
from src.message_handler import send_ads_to_groups, schedule_ads
import os

# Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Add your bot token in the .env file
API_ID = 22318470  # Replace with your actual API ID
API_HASH = "cf907c4c2d677b9f67d32828d891e97a"  # Replace with your actual API hash
OWNER_ID = os.getenv("OWNER_ID")  # Add your Telegram user ID in the .env file

# Initialize Telegram Bot Client
bot = TelegramClient("SpinifyBot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    user = await event.get_sender()
    await event.reply(
        f"🌟 **Welcome to Spinify, {user.first_name}!**\n\n"
        "**Commands:**\n"
        "- `/login`: Log in to manage your account.\n"
        "- `/approve <user_id>`: Approve a user (owner only).\n"
        "- `/add_group <group_username>`: Add a group to send ads.\n"
        "- `/list_groups`: List your added groups.\n"
        "- `/send_ads <message>`: Send a message to all added groups.\n"
        "- `/set_ads_message <message>`: Schedule a recurring ad.\n\n"
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

@bot.on(events.NewMessage(pattern=r"/add_group (.+)"))
async def handle_add_group_command(event):
    user_id = str(event.sender_id)
    group_username = event.pattern_match.group(1)
    await handle_add_group(event, user_id, group_username)

@bot.on(events.NewMessage(pattern="/list_groups"))
async def handle_list_groups_command(event):
    user_id = str(event.sender_id)
    await handle_list_groups(event, user_id)

@bot.on(events.NewMessage(pattern=r"/send_ads (.+)"))
async def handle_send_ads(event):
    user_id = str(event.sender_id)
    message = event.pattern_match.group(1)
    result = await send_ads_to_groups(user_id, message)
    await event.reply(result)

@bot.on(events.NewMessage(pattern=r"/set_ads_message (.+)"))
async def handle_set_ads_message(event):
    user_id = str(event.sender_id)
    message = event.pattern_match.group(1)

    await event.reply("⏱️ **Enter the time frame in hours (e.g., `1` for 1 hour):**")
    time_frame_event = await bot.wait_for(events.NewMessage(from_user=user_id))
    try:
        interval_hours = int(time_frame_event.message)
        result = schedule_ads(user_id, message, interval_hours)
        await event.reply(result)
    except ValueError:
        await event.reply("❌ **Invalid time frame. Please enter a valid number.**")
