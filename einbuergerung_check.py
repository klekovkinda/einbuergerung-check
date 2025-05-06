import os
from datetime import datetime

import telebot

from lib.collect_statistics import add_record
from lib.status_check import check_for_appointment, CheckStatus
from lib.utils import build_html_message

URL = "https://service.berlin.de/terminvereinbarung/termin/all/351180/"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

print("Checking...")
date_time_now = datetime.now()
timestamp = date_time_now.strftime("%Y%m%d_%H%M%S")
appointment_status, available_dates = check_for_appointment(URL, timestamp, delay=3)

if appointment_status == CheckStatus.APPOINTMENTS_AVAILABLE:
    html_message = build_html_message(URL, available_dates)
    bot.send_message(TELEGRAM_CHAT_ID, html_message, parse_mode="HTML")
    print(f"Telegram bot notification sent:\n{html_message}")

csv_filename = f"output/statistics/stat_{date_time_now.strftime('%Y%m')}.csv"
execution_time = date_time_now.strftime('%Y-%m-%d %H:%M:%S')
add_record(csv_filename, execution_time, appointment_status, available_dates)
