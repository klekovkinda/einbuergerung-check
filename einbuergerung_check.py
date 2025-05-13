import os
from datetime import datetime

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from lib.channel_operator import get_channel_members, delete_unpinned_messages
from lib.collect_statistics import add_record, add_missing_users
from lib.status_check import check_for_appointment, CheckStatus
from lib.utils import build_html_message

SERVICE_URL = "https://service.berlin.de/terminvereinbarung/termin/all/351180/"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

print("Checking...")
date_time_now = datetime.now()
timestamp = date_time_now.strftime("%Y%m%d_%H%M%S")
appointment_status, available_dates = check_for_appointment(SERVICE_URL, timestamp, delay=3)

if appointment_status == CheckStatus.APPOINTMENTS_AVAILABLE:
    html_message = build_html_message(available_dates)
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="Click here to book the appointment", url=SERVICE_URL))

    bot.send_message(TELEGRAM_CHAT_ID, html_message, parse_mode="HTML", reply_markup=keyboard)
    print(f"Telegram bot notification sent with button:\n{html_message}")
elif appointment_status == CheckStatus.NO_APPOINTMENTS:
    delete_unpinned_messages(TELEGRAM_CHAT_ID)

csv_stat_filename = f"output/statistics/stat_{date_time_now.strftime('%Y%m%d')}.csv"
csv_user_filename = f"output/statistics/user_{date_time_now.strftime('%Y%m%d')}.csv"
execution_time = date_time_now.strftime('%Y-%m-%d %H:%M:%S')
add_record(csv_stat_filename, execution_time, appointment_status, available_dates)
add_missing_users(csv_user_filename, get_channel_members(TELEGRAM_CHAT_ID))
