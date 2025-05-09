import csv
import os
from datetime import datetime, timedelta, timezone

import pytz
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from lib.status_check import CheckStatus

SUPPORT_URL = "https://buymeacoffee.com/termin_radar"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


def build_html_message(start_at: str = "00:00:00", finish_at: str = "00:00:00", execution_times: int = 0,
                       successful_notifications: int = 0, available_dates: int = 0, failed_requests: int = 0):
    return (f"""
    Hey friends!
    I'm <strong>Termin Radar 😎</strong> While you were waiting yesterday, I wasn’t just twiddling my thumbs — I was scanning like crazy for available Einbürgerungstest appointments!
    Between <strong>{start_at}</strong> and <strong>{finish_at}</strong>, I checked <strong>{execution_times}</strong> times.
    I managed to find open slots and sent you <strong>{successful_notifications}</strong> notifications for <strong>{available_dates}</strong> different dates!
    There were <strong>{failed_requests}</strong> times when I couldn’t load the info — sorry about that! But no worries, the team is working hard to improve the service every day.
    Like what I'm doing? You can support the project and help me keep scanning for you! 🙌
    """)


def read_yesterday_stats() -> tuple[str, str, int, int, int, int]:
    start_at = "00:00:00"
    finish_at = "00:00:00"
    execution_times_count = 0
    successful_notifications_count = 0
    available_dates_count = 0
    failed_requests_count = 0

    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    file_name = f"stat_{yesterday}.csv"
    file_path = os.path.join("output", "statistics", file_name)

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return start_at, finish_at, execution_times_count, successful_notifications_count, available_dates_count, failed_requests_count

    berlin_tz = pytz.timezone('Europe/Berlin')
    utc_tz = timezone.utc

    execution_times = set()
    successful_notifications = set()
    available_dates = set()
    failed_requests = set()

    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            utc_time = datetime.strptime(row['execution_time'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=utc_tz)
            berlin_time = utc_time.astimezone(berlin_tz)
            execution_times.add(berlin_time)
            if row['status'] == CheckStatus.APPOINTMENTS_AVAILABLE.value:
                successful_notifications.add(row['execution_time'])
                available_dates.add(row['appointmentdate'])
            elif row['status'] != CheckStatus.NO_APPOINTMENTS.value:
                failed_requests.add(row['execution_time'])

    if execution_times:
        start_at = min(execution_times).strftime('%H:%M:%S')
        finish_at = max(execution_times).strftime('%H:%M:%S')
        execution_times_count = len(execution_times)
        successful_notifications_count = len(successful_notifications)
        available_dates_count = len(available_dates)
        failed_requests_count = len(failed_requests)
    else:
        print("No data found in the file.")

    return start_at, finish_at, execution_times_count, successful_notifications_count, available_dates_count, failed_requests_count


if __name__ == "__main__":
    html_message = build_html_message(*read_yesterday_stats())
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="Click here to support the project", url=SUPPORT_URL))

    try:
        bot.unpin_all_chat_messages(TELEGRAM_CHAT_ID)
        print("All messages unpinned successfully.")
    except Exception as e:
        print(f"Failed to unpin messages: {e}")

    sent_message = bot.send_message(TELEGRAM_CHAT_ID, html_message, parse_mode="HTML", reply_markup=keyboard)
    print(f"Telegram bot statistic sent with button:\n{html_message}")

    try:
        bot.pin_chat_message(TELEGRAM_CHAT_ID, sent_message.message_id)
        print("Message pinned successfully.")
    except Exception as e:
        print(f"Failed to pin the message: {e}")

