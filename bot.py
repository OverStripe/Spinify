import os
import time
import pickle
import logging
import telebot
from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError

# 🌟 Load Environment Variables
load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Telegram Bot Token
OWNER_ID = int(os.getenv("OWNER_ID"))
DEFAULT_INTERVAL = int(os.getenv("DEFAULT_INTERVAL", 600))  # Default: 10 min
DATA_FILE = "bot_data.pkl"

# 🌟 Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# 🌟 Initialize Telethon Client
if SESSION_STRING:
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
else:
    client = TelegramClient("user_session", API_ID, API_HASH)

# 🌟 Connect to Telegram
client.connect()

# 🌟 If not authorized, log in manually
if not client.is_user_authorized():
    logger.info("🔑 Logging in manually...")
    client.send_code_request(PHONE_NUMBER)
    code = input("Enter the login code: ")
    client.sign_in(PHONE_NUMBER, code)

logger.info("✅ Logged in successfully!")

# 🌟 Initialize Telegram Bot (for management)
bot = telebot.TeleBot(BOT_TOKEN)

# 🌟 Global Variables
group_list = {}  # Stores group names and intervals
ad_message = "🚀 Boost your business with exclusive deals! Contact us now!"

# 🌟 Load Data from File
def load_data():
    global group_list, ad_message
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "rb") as f:
            data = pickle.load(f)
            group_list = data.get("group_list", {})
            ad_message = data.get("ad_message", ad_message)
        logger.info("📁 Data Loaded Successfully!")

# 🌟 Save Data Persistently
def save_data():
    with open(DATA_FILE, "wb") as f:
        pickle.dump({"group_list": group_list, "ad_message": ad_message}, f)
    logger.info("📁 Data Saved Successfully!")

# 🌟 Fetch Joined Groups Automatically
def fetch_groups():
    """Fetch all joined groups and add them to the list."""
    logger.info("🔍 Fetching joined groups...")
    group_list.clear()
    for dialog in client.iter_dialogs():
        if dialog.is_group:
            group_list[dialog.id] = DEFAULT_INTERVAL
            logger.info(f"✅ Added Group: {dialog.name} ({dialog.id})")
    save_data()
    return len(group_list)

# 🌟 Post Ads to Groups
def post_ads():
    """Sends ads to all joined groups."""
    logger.info("🚀 Starting Ad Posting...")
    for group_id in group_list.keys():
        try:
            client.send_message(group_id, ad_message)
            logger.info(f"✅ Ad Sent to {group_id}")
            time.sleep(10)  # Prevent spam bans
        except FloodWaitError as e:
            logger.warning(f"⚠️ FLOOD_WAIT Error! Cooling Down for {e.seconds} Seconds.")
            time.sleep(e.seconds)  # Wait before retrying
        except Exception as e:
            logger.warning(f"⚠️ Failed to send message to {group_id}: {e}")

# 🌟 Set Ad Message
def set_ad(new_ad):
    """Updates the ad message."""
    global ad_message
    ad_message = new_ad
    save_data()
    logger.info("✅ Ad Message Updated!")

# 🌟 Telegram Bot Commands
@bot.message_handler(commands=["start"])
def start(message):
    """Handles the /start command."""
    if message.chat.id == OWNER_ID:
        bot.send_message(message.chat.id, "🌟 Welcome to the Telegram Ad Bot! Use /help for commands.")
    else:
        bot.send_message(message.chat.id, "❌ Unauthorized!")

@bot.message_handler(commands=["help"])
def help_command(message):
    """Shows available commands."""
    if message.chat.id == OWNER_ID:
        bot.send_message(message.chat.id,
            "🔹 **Available Commands:**\n"
            "/fetch_groups - Fetch joined groups\n"
            "/list_groups - Show all groups\n"
            "/set_ad <message> - Set new ad message\n"
            "/post - Post ad to all groups"
        )

@bot.message_handler(commands=["fetch_groups"])
def fetch_groups_command(message):
    """Handles /fetch_groups command."""
    if message.chat.id == OWNER_ID:
        count = fetch_groups()
        bot.send_message(message.chat.id, f"✅ {count} groups fetched successfully!")

@bot.message_handler(commands=["list_groups"])
def list_groups_command(message):
    """Handles /list_groups command."""
    if message.chat.id == OWNER_ID:
        if not group_list:
            bot.send_message(message.chat.id, "📂 No groups found! Run /fetch_groups first.")
        else:
            groups = "\n".join([f"🔹 `{gid}`" for gid in group_list.keys()])
            bot.send_message(message.chat.id, f"📂 **Joined Groups:**\n{groups}")

@bot.message_handler(commands=["set_ad"])
def set_ad_command(message):
    """Handles /set_ad command."""
    if message.chat.id == OWNER_ID:
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            bot.send_message(message.chat.id, "⚠️ Usage: `/set_ad Your Ad Message`")
            return
        
        set_ad(args[1].strip())
        bot.send_message(message.chat.id, "✅ **Ad Message Updated!**")

@bot.message_handler(commands=["post"])
def post_ads_command(message):
    """Handles /post command."""
    if message.chat.id == OWNER_ID:
        bot.send_message(message.chat.id, "📢 **Posting Ads...**")
        post_ads()
        bot.send_message(message.chat.id, "✅ **Ad Sent to All Groups!**")

# 🌟 Load Data and Start Bot
load_data()
bot.polling()
