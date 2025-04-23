from lib.status_check import check_for_appointment
import telebot
import os

URL = "https://service.berlin.de/terminvereinbarung/termin/all/351180/"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

print("Checking...", end="", flush=True)
if check_for_appointment(URL, saving_for_analysis=True):
    bot.send_message(TELEGRAM_CHAT_ID, f"Go and book your appointment now! \n {URL}")
    print("Telegram bot notification sent.")
