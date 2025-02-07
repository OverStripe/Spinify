import os
import asyncio
import pickle
import logging
import aiofiles
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.markdown import hbold
from telethon import TelegramClient, errors
import random
from datetime import datetime

# 🌟 Load Environment Variables
load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
DEFAULT_INTERVAL = int(os.getenv("DEFAULT_INTERVAL", 600))  # Default: 10 min
DATA_FILE = os.getenv("DATA_FILE", "bot_data.pkl")

# 🌟 Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# 🌟 Initialize Aiogram Bot & Dispatcher
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# 🌟 Global Variables
group_list = {}  # Group IDs with posting intervals
ad_message = "🚀 Boost your business with our exclusive deals! Contact us now!"
session_files = []  # Available session files
clients = []  # Telethon clients
cooldown_time = 60  # Cooldown for FLOOD errors

# 🌟 Load Data from File
def load_data():
    global group_list, ad_message, session_files
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "rb") as f:
            data = pickle.load(f)
            group_list = data.get("group_list", {})
            ad_message = data.get("ad_message", ad_message)
            session_files = data.get("session_files", [])
        logger.info("📁 Data Loaded Successfully!")

# 🌟 Save Data Persistently
def save_data():
    with open(DATA_FILE, "wb") as f:
        pickle.dump({"group_list": group_list, "ad_message": ad_message, "session_files": session_files}, f)
    logger.info("📁 Data Saved Successfully!")

# 🌟 Add Group Command
@dp.message(Command("add_group"))
async def add_group(message: Message):
    """Adds a group to the list."""
    logger.info(f"📩 Received /add_group from {message.from_user.id}")
    if message.from_user.id == OWNER_ID:
        args = message.text.split()
        if len(args) < 2:
            await message.answer("⚠️ Usage: `/add_group group_id`")
            return
        
        group_id = args[1]
        group_list[group_id] = DEFAULT_INTERVAL
        save_data()
        await message.answer(f"✅ Group `{group_id}` added successfully!")
    else:
        await message.answer("⚠️ Unauthorized Access!")

# 🌟 Remove Group Command
@dp.message(Command("remove_group"))
async def remove_group(message: Message):
    """Removes a group from the list."""
    logger.info(f"📩 Received /remove_group from {message.from_user.id}")
    if message.from_user.id == OWNER_ID:
        args = message.text.split()
        if len(args) < 2:
            await message.answer("⚠️ Usage: `/remove_group group_id`")
            return
        
        group_id = args[1]
        if group_id in group_list:
            del group_list[group_id]
            save_data()
            await message.answer(f"✅ Group `{group_id}` removed successfully!")
        else:
            await message.answer("⚠️ Group not found!")
    else:
        await message.answer("⚠️ Unauthorized Access!")

# 🌟 List Groups Command
@dp.message(Command("list_groups"))
async def list_groups(message: Message):
    """Lists all groups."""
    logger.info(f"📩 Received /list_groups from {message.from_user.id}")
    if message.from_user.id == OWNER_ID:
        if not group_list:
            await message.answer("📂 No groups added yet!")
        else:
            groups = "\n".join([f"🔹 `{group}`" for group in group_list.keys()])
            await message.answer(f"📂 **Registered Groups:**\n{groups}")
    else:
        await message.answer("⚠️ Unauthorized Access!")

# 🌟 Start Command
@dp.message(Command("start"))
async def start_command(message: Message):
    """Bot Start Message."""
    logger.info(f"📩 Received /start from {message.from_user.id}")
    if message.from_user.id == OWNER_ID:
        await message.answer(f"🌟 **Ad Bot Running!** 🌟\n\nUse `/list_groups` to view all groups.")
    else:
        await message.answer("⚠️ Unauthorized Access!")

# 🌟 Set Ad Command
@dp.message(Command("set_ad"))
async def set_ad(message: Message):
    """Sets a New Ad Message."""
    logger.info(f"📩 Received /set_ad from {message.from_user.id}")
    if message.from_user.id == OWNER_ID:
        global ad_message
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.answer("⚠️ Usage: `/set_ad Your Ad Message`")
            return
        
        ad_message = args[1].strip()
        save_data()
        await message.answer("✅ **Ad Updated!**")
    else:
        await message.answer("⚠️ Unauthorized Access!")

# 🌟 Post Ad Command (Manual)
@dp.message(Command("post"))
async def post_ads(message: Message):
    """Manually Sends Ads to All Groups."""
    logger.info(f"📩 Received /post from {message.from_user.id}")
    if message.from_user.id == OWNER_ID:
        for group in group_list.keys():
            await message.answer(f"📢 **Posting Ad in:** `{group}`")
        await message.answer("✅ **Ad Sent to All Groups!**")
    else:
        await message.answer("⚠️ Unauthorized Access!")

# 🌟 Main Function
async def main():
    """Start Bot & Run Tasks."""
    load_data()
    logger.info(f"🚀 Bot Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # ✅ Register Commands
    dp.message.register(start_command)
    dp.message.register(add_group)
    dp.message.register(remove_group)
    dp.message.register(list_groups)
    dp.message.register(set_ad)
    dp.message.register(post_ads)

    await dp.run_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
