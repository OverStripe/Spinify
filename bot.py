import asyncio
import time
import sqlite3
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Configuration
API_ID = "22318470"
API_HASH = "cf907c4c2d677b9f67d32828d891e97a"
BOT_TOKEN = "7076580983:AAG-ksR-tsvXEM3L2eEGl1qPv2OXB0ezJls"
OWNER_ID = 7222795580  # Replace with your Telegram ID
DEFAULT_INTERVAL = 10  # Default posting interval (minutes)

# Database Setup
conn = sqlite3.connect("ads_bot.db")
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS group_intervals (group_id TEXT PRIMARY KEY, interval_minutes INTEGER DEFAULT 10)")
cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, session_string TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS ads (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, ad_text TEXT, next_post_time INTEGER)")
cursor.execute("CREATE TABLE IF NOT EXISTS groups (group_id TEXT PRIMARY KEY)")
cursor.execute("CREATE TABLE IF NOT EXISTS approved_users (user_id INTEGER PRIMARY KEY)")

conn.commit()
conn.close()

# Bot Setup
bot = Client("ads_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Async Task Scheduler
scheduler = AsyncIOScheduler()

# ----------------------------------
#  🚀 COMMANDS
# ----------------------------------

@bot.on_message(filters.command("start") & filters.private)
async def start_command(_, message: Message):
    await message.reply_text("🚀 **Welcome!**\nThis bot auto-posts ads using your Telegram accounts.\n\nUse `/help` to see available commands.")

@bot.on_message(filters.command("help") & filters.private)
async def help_command(_, message: Message):
    help_text = """
🚀 **Command List**
🔹 `/start` - Welcome message
🔹 `/help` - Show available commands
🔹 `/addaccount {session_string}` - Add Telegram account
🔹 `/schedule {ad_message}` - Schedule an ad
🔹 `/myschedule` - View scheduled ads
🔹 `/cancel {ad_id}` - Cancel an ad
🔹 `/profile` - View linked accounts
🔹 `/setinterval {group_id} {minutes}` - Set group interval (Admin)
🔹 `/addgroup {group_id}` - Add a group (Admin)
🔹 `/getinterval {group_id}` - Check group interval (Admin)
🔹 `/listgroups` - View all groups (Admin)
🔹 `/approve {user_id}` - Approve a user (Admin)
"""
    await message.reply_text(help_text)

@bot.on_message(filters.command("addaccount") & filters.private)
async def add_account(_, message: Message):
    args = message.text.split(" ", 1)
    if len(args) < 2:
        return await message.reply("⚠️ Usage: `/addaccount {session_string}`")
    session_string = args[1]
    user_id = message.from_user.id

    conn = sqlite3.connect("ads_bot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO users (user_id, session_string) VALUES (?, ?)", (user_id, session_string))
    conn.commit()
    conn.close()

    await message.reply("✅ **Account added successfully!** You can now schedule ads.")

@bot.on_message(filters.command("schedule") & filters.private)
async def schedule_ad(_, message: Message):
    args = message.text.split(" ", 1)
    if len(args) < 2:
        return await message.reply("⚠️ Usage: `/schedule {ad_message}`")

    user_id = message.from_user.id
    ad_text = args[1]
    next_post_time = int(time.time())

    conn = sqlite3.connect("ads_bot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO ads (user_id, ad_text, next_post_time) VALUES (?, ?, ?)", (user_id, ad_text, next_post_time))
    conn.commit()
    conn.close()

    await message.reply("✅ **Ad scheduled for auto-posting!**")

@bot.on_message(filters.command("setinterval") & filters.private)
async def set_interval(_, message: Message):
    if message.from_user.id != OWNER_ID:
        return await message.reply("❌ Only the bot owner can set group intervals.")

    args = message.text.split(" ", 2)
    if len(args) < 3:
        return await message.reply("⚠️ Usage: `/setinterval {group_id} {minutes}`")

    group_id, interval_minutes = args[1], int(args[2])
    conn = sqlite3.connect("ads_bot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO group_intervals (group_id, interval_minutes) VALUES (?, ?)", (group_id, interval_minutes))
    conn.commit()
    conn.close()

    await message.reply(f"✅ **Interval for Group `{group_id}` set to {interval_minutes} minutes!**")

@bot.on_message(filters.command("listgroups") & filters.private)
async def list_groups(_, message: Message):
    conn = sqlite3.connect("ads_bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT group_id FROM groups")
    groups = cursor.fetchall()
    conn.close()

    if not groups:
        return await message.reply("⚠️ No groups available.")

    group_list = "\n".join([f"📌 {g[0]}" for g in groups])
    await message.reply(f"📌 **Groups List:**\n\n{group_list}")

# ----------------------------------
#  🚀 AUTO POSTING FUNCTION
# ----------------------------------

async def auto_post_ads():
    while True:
        conn = sqlite3.connect("ads_bot.db")
        cursor = conn.cursor()

        current_time = int(time.time())
        cursor.execute("SELECT id, user_id, ad_text FROM ads WHERE next_post_time <= ?", (current_time,))
        ads = cursor.fetchall()
        cursor.execute("SELECT group_id FROM groups")
        groups = cursor.fetchall()
        conn.close()

        if ads and groups:
            for ad in ads:
                ad_id, user_id, ad_text = ad

                conn = sqlite3.connect("ads_bot.db")
                cursor = conn.cursor()
                cursor.execute("SELECT session_string FROM users WHERE user_id = ?", (user_id,))
                user_sessions = cursor.fetchall()
                conn.close()

                if user_sessions:
                    for session in user_sessions:
                        async with TelegramClient(StringSession(session[0]), API_ID, API_HASH) as client:
                            for group in groups:
                                group_id = group[0]
                                cursor.execute("SELECT interval_minutes FROM group_intervals WHERE group_id = ?", (group_id,))
                                interval_minutes = cursor.fetchone()[0] if cursor.fetchone() else DEFAULT_INTERVAL
                                await client.send_message(int(group_id), ad_text)
                                await asyncio.sleep(interval_minutes * 60)

        await asyncio.sleep(60)

# Start Auto Posting
scheduler.add_job(auto_post_ads, "interval", seconds=60)
scheduler.start()

# Start the bot
bot.run()
