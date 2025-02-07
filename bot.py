import os
import asyncio
import pickle
import logging
import aiofiles
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message, Document
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
group_list = {}
ad_message = "🚀 Boost your business with our exclusive deals! Contact us now!"
session_files = []  # Available session files
clients = []  # Telethon clients
cooldown_time = 60  # Cooldown for FLOOD errors

# 🌟 Default Telegram Client (Used If No Other Accounts Exist)
default_client = TelegramClient("default_session", API_ID, API_HASH)

async def start_default_client():
    """Start the default Telegram account if no sessions exist."""
    await default_client.start()
    clients.append(default_client)
    logger.info("🌟 Default Telegram Account Initialized!")

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

async def load_sessions():
    """Load Telegram session files dynamically and fetch joined groups."""
    global clients, group_list
    clients.clear()
    
    for session_file in session_files:
        client = TelegramClient(session_file, API_ID, API_HASH)
        await client.start()
        clients.append(client)
        logger.info(f"🌟 Loaded Session: {session_file}")

        # 🌟 Fetch and add joined groups
        async for dialog in client.iter_dialogs():
            if dialog.is_group:
                group_list[dialog.entity.id] = DEFAULT_INTERVAL

    # If No Sessions Exist, Use Default Account
    if not clients:
        await start_default_client()

async def send_message_with_retry(client, group):
    """Sends a message with error handling & cooldowns."""
    global cooldown_time
    try:
        async with client:
            await client.send_message(group, ad_message)
            logger.info(f"✅ Ad Sent to {group} Using {client.session.filename}")
            return True
    except errors.FloodWaitError as e:
        cooldown_time = min(e.seconds, 600)  # Max 10 min cooldown
        logger.warning(f"⚠️ FLOOD_WAIT Error! Cooling Down for {cooldown_time} Seconds.")
        await asyncio.sleep(cooldown_time)
        return False
    except Exception as e:
        logger.warning(f"⚠️ Error Sending to {group}: {e}")
        return False

async def scheduled_ad_posting():
    """Handles automatic ad posting with multiple accounts."""
    account_index = 0  # Track Active Account

    while True:
        if not clients:
            logger.warning("⚠️ No Telegram Accounts Available! Using Default Account.")
            await start_default_client()

        for group, interval in group_list.items():
            client = clients[account_index % len(clients)]  # Rotate Accounts
            account_index += 1

            if not await send_message_with_retry(client, group):
                await asyncio.sleep(10)

            await asyncio.sleep(interval + random.randint(5, 20))  # Random Jitter to Avoid Spam Detection

# 🌟 Start Command
@dp.message(Command("start"))
async def start_command(message: Message):
    """Bot Start Message with UI."""
    if message.from_user.id == OWNER_ID:
        await message.answer(f"🌟 **Ad Bot Running!** 🌟\n\nUse {hbold('/login session')} to add accounts.")
    else:
        await message.answer("⚠️ Unauthorized Access!")

# 🌟 Login Session Command
@dp.message(Command("login"))
async def login_session(message: Message):
    """Handles Session File Upload Requests."""
    if message.from_user.id == OWNER_ID:
        await message.answer("📂 **Upload Your Telethon Session File (.session) Now!**")
    else:
        await message.answer("⚠️ Unauthorized Access!")

# 🌟 Set Ad Command
@dp.message(Command("set_ad"))
async def set_ad(message: Message):
    """Sets a New Ad Message & Starts Auto Posting."""
    if message.from_user.id == OWNER_ID:
        global ad_message
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.answer("⚠️ Usage: `/set_ad Your Ad Message`")
            return
        
        ad_message = args[1].strip()
        save_data()

        await message.answer("✅ **Ad Updated & Auto Posting Started!**")
    else:
        await message.answer("⚠️ Unauthorized Access!")

# 🌟 Post Ad Command (Manual)
@dp.message(Command("post"))
async def post_ads(message: Message):
    """Manually Sends Ads to All Groups."""
    if message.from_user.id == OWNER_ID:
        for group in group_list.keys():
            client = random.choice(clients) if clients else default_client
            await send_message_with_retry(client, group)
        await message.answer("✅ **Ad Manually Sent to All Groups!**")
    else:
        await message.answer("⚠️ Unauthorized Access!")

# 🌟 Main Function
async def main():
    """Start Bot & Run Tasks."""
    load_data()
    await load_sessions()
    logger.info(f"🚀 Bot Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    asyncio.create_task(scheduled_ad_posting())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
