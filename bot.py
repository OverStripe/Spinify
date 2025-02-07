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
from telethon.sessions import StringSession
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
session_strings = {}  # Stores session strings {telegram_id: session_string}
clients = {}  # Stores Telethon clients {telegram_id: TelegramClient}
cooldown_time = 60  # Cooldown for FLOOD errors

# 🌟 Save Data Persistently
def save_data():
    with open(DATA_FILE, "wb") as f:
        pickle.dump({"group_list": group_list, "ad_message": ad_message, "session_strings": session_strings}, f)
    logger.info("📁 Data Saved Successfully!")

# 🌟 Load Data
def load_data():
    global group_list, ad_message, session_strings
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "rb") as f:
            data = pickle.load(f)
            group_list = data.get("group_list", {})
            ad_message = data.get("ad_message", ad_message)
            session_strings = data.get("session_strings", {})
        logger.info("📁 Data Loaded Successfully!")

# 🌟 Login Session via Session String
@dp.message(Command("login_session"))
async def login_session(message: Message):
    """Logs in using a Telethon session string."""
    logger.info(f"📩 Received /login_session from {message.from_user.id}")
    if message.from_user.id == OWNER_ID:
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.answer("⚠️ Usage: `/login_session session_string`")
            return
        
        session_string = args[1].strip()
        try:
            client = TelegramClient(StringSession(session_string), API_ID, API_HASH)
            await client.connect()
            if not await client.is_user_authorized():
                await message.answer("⚠️ Invalid Session ID. Please check and try again.")
                return

            session_strings[message.from_user.id] = session_string
            clients[message.from_user.id] = client
            save_data()
            await message.answer("✅ **Session added successfully!** Your ads will now be sent using this Telegram account.")
        except Exception as e:
            logger.error(f"⚠️ Error logging in: {e}")
            await message.answer("⚠️ Error logging in. Please check your session string.")

# 🌟 List Accounts
@dp.message(Command("list_accounts"))
async def list_accounts(message: Message):
    """Lists logged-in accounts."""
    logger.info(f"📩 Received /list_accounts from {message.from_user.id}")
    if message.from_user.id == OWNER_ID:
        if not session_strings:
            await message.answer("📂 No accounts logged in yet!")
        else:
            accounts = "\n".join([f"🔹 `{tg_id}`" for tg_id in session_strings.keys()])
            await message.answer(f"📂 **Logged-in Accounts:**\n{accounts}")
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

# 🌟 Send Message with Retry
async def send_message_with_retry(client, group):
    """Sends a message with error handling & cooldowns."""
    global cooldown_time
    try:
        await client.send_message(group, ad_message)
        logger.info(f"✅ Ad Sent to {group}")
        return True
    except errors.FloodWaitError as e:
        cooldown_time = min(e.seconds, 600)  # Max 10 min cooldown
        logger.warning(f"⚠️ FLOOD_WAIT Error! Cooling Down for {cooldown_time} Seconds.")
        await asyncio.sleep(cooldown_time)
        return False
    except Exception as e:
        logger.warning(f"⚠️ Error Sending to {group}: {e}")
        return False

# 🌟 Post Ad Command (Manual)
@dp.message(Command("post"))
async def post_ads(message: Message):
    """Manually Sends Ads to All Groups."""
    logger.info(f"📩 Received /post from {message.from_user.id}")
    if message.from_user.id == OWNER_ID:
        if not clients:
            await message.answer("⚠️ No Telegram sessions logged in! Use `/login_session` first.")
            return
        
        client = clients.get(message.from_user.id)
        if not client:
            await message.answer("⚠️ No active session for your Telegram ID.")
            return
        
        for group in group_list.keys():
            await send_message_with_retry(client, group)
        await message.answer("✅ **Ad Sent to All Groups!**")
    else:
        await message.answer("⚠️ Unauthorized Access!")

# 🌟 Main Function
async def main():
    """Start Bot & Run Tasks."""
    load_data()
    logger.info(f"🚀 Bot Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # ✅ Register Handlers
    dp.message.register(login_session)
    dp.message.register(list_accounts)
    dp.message.register(set_ad)
    dp.message.register(post_ads)

    await dp.run_polling(bot)

# ✅ **Prevent RuntimeError: asyncio.run() cannot be called from a running event loop**
if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            logger.warning("⚠️ Event loop already running. Using create_task().")
            loop.create_task(main())
        else:
            loop.run_until_complete(main())
    except RuntimeError:
        asyncio.run(main())
