import os
import time
import pickle
import logging
import telebot
import schedule
import threading
from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError

# Load Environment Variables
load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
DEFAULT_INTERVAL = int(os.getenv("DEFAULT_INTERVAL", 600))
LOG_CHAT_ID = int(os.getenv("LOG_CHAT_ID"))
DATA_FILE = "bot_data.pkl"
SESSION_FILE = "session.pkl"
APPROVED_USERS_FILE = "approved_users.pkl"

# Initialize Telegram Bot
bot = telebot.TeleBot(BOT_TOKEN)

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_log(message):
    """Sends logs to Telegram Chat"""
    try:
        bot.send_message(LOG_CHAT_ID, f"▪ **LOG:** {message}", parse_mode="Markdown")
    except Exception as e:
        print(f"ERROR: Failed to send log: {e}")

# Global Variables
client = None
group_list = {}
ad_message = os.getenv("DEFAULT_AD_MESSAGE", "▪ New Promotion ▪\n\nBoost your business! Contact @YourUsername")
approved_users = set()

# Load Approved Users
def load_approved_users():
    global approved_users
    if os.path.exists(APPROVED_USERS_FILE):
        with open(APPROVED_USERS_FILE, "rb") as f:
            approved_users = pickle.load(f)
    send_log("✔ Approved Users Loaded")

# Save Approved Users
def save_approved_users():
    with open(APPROVED_USERS_FILE, "wb") as f:
        pickle.dump(approved_users, f)
    send_log("✔ Approved Users Updated")

# Approve New Users
@bot.message_handler(commands=["approve"])
def approve_user(message):
    if message.chat.id == OWNER_ID:
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            bot.send_message(message.chat.id, "Usage: `/approve <user_id>`", parse_mode="Markdown")
            return
        
        user_id = int(args[1].strip())
        approved_users.add(user_id)
        save_approved_users()
        bot.send_message(message.chat.id, f"✔ User {user_id} Approved", parse_mode="Markdown")
        send_log(f"✔ User {user_id} Approved by Owner")
    else:
        bot.send_message(message.chat.id, "✖ You are not authorized", parse_mode="Markdown")

# Check if User is Approved
def is_user_approved(user_id):
    return user_id in approved_users or user_id == OWNER_ID

# Save & Load Ad Message
def save_ad_message():
    with open(DATA_FILE, "wb") as f:
        pickle.dump({"group_list": group_list, "ad_message": ad_message}, f)
    send_log("✔ Ad Message Updated")

def load_ad_message():
    global ad_message
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "rb") as f:
            data = pickle.load(f)
            ad_message = data.get("ad_message", ad_message)

# Set Ad Message
@bot.message_handler(commands=["set_ad"])
def set_ad_command(message):
    if message.chat.id == OWNER_ID:
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            bot.send_message(message.chat.id, "Usage: `/set_ad <message>`", parse_mode="Markdown")
            return
        
        global ad_message
        ad_message = args[1].strip()
        save_ad_message()
        bot.send_message(message.chat.id, "✔ Ad Message Updated")
        send_log(f"✔ New Ad Message Set:\n{ad_message}")
    else:
        bot.send_message(message.chat.id, "✖ You are not authorized", parse_mode="Markdown")

# Set Group Interval
@bot.message_handler(commands=["set"])
def set_group_interval(message):
    if is_user_approved(message.chat.id):
        args = message.text.split(maxsplit=2)
        if len(args) < 3:
            bot.send_message(message.chat.id, "Usage: `/set <group_id> <interval_in_seconds>`", parse_mode="Markdown")
            return
        
        group_id = int(args[1])
        interval = int(args[2])
        if group_id in group_list:
            group_list[group_id] = interval
            save_ad_message()
            bot.send_message(message.chat.id, f"✔ Interval Updated: {interval}s for {group_id}", parse_mode="Markdown")
            send_log(f"✔ Interval Updated for {group_id}: {interval}s")
        else:
            bot.send_message(message.chat.id, "✖ Group not found", parse_mode="Markdown")

# Post Ads
def post_ads():
    send_log("▪ Posting Ads")
    for group_id, interval in group_list.items():
        try:
            formatted_ad = f"```▪ New Promotion ▪```\n\n{ad_message}"
            client.send_message(group_id, formatted_ad, parse_mode="Markdown")
            send_log(f"✔ Ad Sent to {group_id}")
            time.sleep(10)
        except FloodWaitError as e:
            send_log(f"✖ FLOOD_WAIT {e.seconds}s")
            time.sleep(e.seconds)
        except Exception as e:
            send_log(f"✖ Failed to send ad to {group_id}")

# Telegram Bot Commands
@bot.message_handler(commands=["post"])
def post_ads_command(message):
    if message.chat.id == OWNER_ID:
        bot.send_message(message.chat.id, "▪ Posting Ads")
        post_ads()
        bot.send_message(message.chat.id, "✔ Ad Sent to All Groups")

# Start Scheduler
def start_scheduler():
    send_log("▪ Scheduler Started")
    schedule_thread = threading.Thread(target=schedule.run_pending, daemon=True)
    schedule_thread.start()

# Load Data and Start Bot
load_ad_message()
load_approved_users()
start_scheduler()
bot.polling()
