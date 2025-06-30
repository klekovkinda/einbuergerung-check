import os
from datetime import datetime

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from lib.collect_statistics import add_record, add_missing_users, add_dynamodb_record
from lib.get_channel_members import get_channel_members
from lib.status_check import check_for_appointment, CheckStatus
from lib.utils import build_html_message

SERVICE_URL = "https://service.berlin.de/terminvereinbarung/termin/all/351180/"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

print("Checking...")
execution_date_time = datetime.now()
timestamp = execution_date_time.strftime("%Y%m%d_%H%M%S")
appointment_status, available_dates = check_for_appointment(SERVICE_URL, timestamp, delay=3)

if appointment_status == CheckStatus.APPOINTMENTS_AVAILABLE:
    html_message = build_html_message(available_dates)
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="Click here to book the appointment", url=SERVICE_URL))

    bot.send_message(TELEGRAM_CHAT_ID, html_message, parse_mode="HTML", reply_markup=keyboard)
    print(f"Telegram bot notification sent with button:\n{html_message}")

csv_stat_filename = f"output/statistics/stat_{execution_date_time.strftime('%Y%m%d')}.csv"
csv_user_filename = f"output/statistics/user_{execution_date_time.strftime('%Y%m%d')}.csv"
execution_time = execution_date_time.strftime('%Y-%m-%d %H:%M:%S')
add_record(csv_stat_filename, execution_time, appointment_status, available_dates)
add_dynamodb_record("termin_statistic", execution_date_time, appointment_status, available_dates)
add_missing_users(csv_user_filename, get_channel_members(TELEGRAM_CHAT_ID))
