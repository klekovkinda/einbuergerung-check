import os

import telebot

from lib.status_check import check_for_appointment
from lib.utils import build_html_message

URL = "https://service.berlin.de/terminvereinbarung/termin/all/351180/"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

print("Checking...")
appointment_available, available_dates = check_for_appointment(URL, delay=3, saving_for_analysis=True)

if appointment_available:
    html_message = build_html_message(URL, available_dates)
    bot.send_message(TELEGRAM_CHAT_ID, html_message, parse_mode="HTML")
    print(f"Telegram bot notification sent:\n{html_message}")
