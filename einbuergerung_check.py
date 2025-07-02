import os
from datetime import datetime

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from lib.collect_statistics import add_ddb_termin_records, add_ddb_user_records
from lib.get_channel_members import get_channel_members
from lib.status_check import check_for_appointment, CheckStatus
from lib.utils import build_html_message

SERVICE_URL = "https://service.berlin.de/terminvereinbarung/termin/all/351180/"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

print("Checking...")
now_date_time = datetime.now()
timestamp = now_date_time.strftime("%Y%m%d_%H%M%S")
appointment_status, available_dates = check_for_appointment(SERVICE_URL, timestamp, delay=3)

if appointment_status == CheckStatus.APPOINTMENTS_AVAILABLE:
    html_message = build_html_message(available_dates)
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="Click here to book the appointment", url=SERVICE_URL))

    bot.send_message(TELEGRAM_CHAT_ID, html_message, parse_mode="HTML", reply_markup=keyboard)
    print(f"Telegram bot notification sent with button:\n{html_message}")

execution_time = now_date_time.strftime('%Y-%m-%d %H:%M:%S')
channel_members_encrypted = get_channel_members(TELEGRAM_CHAT_ID)

add_ddb_termin_records(now_date_time, appointment_status, available_dates)
add_ddb_user_records(now_date_time, channel_members_encrypted)
