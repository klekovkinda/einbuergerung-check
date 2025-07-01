import csv
import os
from datetime import datetime, timedelta, timezone

import boto3
import pytz
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from lib.collect_statistics import UserStatus
from lib.status_check import CheckStatus
from lib.utils import build_statistics_html_message

SUPPORT_URL = "https://buymeacoffee.com/termin_radar"
PAYPAL_SUPPORT_URL = "https://www.paypal.com/pool/9f1bWcE4aK?sr=wccr"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
dynamodb = boto3.resource("dynamodb")

def get_channel_members_for_date(date_ymd_str) -> tuple[set, set]:
    old_users = set()
    new_users = set()

    file_name = f"user_{date_ymd_str}.csv"
    file_path = os.path.join("output", "statistics", file_name)

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return old_users, new_users

    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['status'] == UserStatus.NEW.value:
                new_users.add(row['user'])
            else:
                old_users.add(row['user'])
    return old_users, new_users

def get_users_for_date(date)-> set[str]:
    table = dynamodb.Table("user_statistic")
    date_ymd_str = date.strftime("%Y-%m-%d")
    response = table.query(KeyConditionExpression=boto3.dynamodb.conditions.Key("date").eq(date_ymd_str))
    return set([item.get('user') for item in response.get('Items', [])])


def read_yesterday_user_stats() -> tuple[int, int]:
    today = datetime.now()
    today_users = get_users_for_date(today)
    yesterday_users = get_users_for_date(today - timedelta(days=1))
    day_before_yesterday_users = get_users_for_date(today - timedelta(days=2))
    yesterday_missing_users = yesterday_users - today_users
    yesterday_new_users = yesterday_users - day_before_yesterday_users
    return len(yesterday_new_users), len(yesterday_missing_users)


def read_yesterday_execution_stats() -> tuple[str, str, int, int, int, int]:
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
            elif row['status'] != CheckStatus.NO_APPOINTMENTS.value and row['status'] != CheckStatus.MAINTENANCE.value:
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
    new_users, missing_users = read_yesterday_user_stats()
    start_at, finish_at, execution_times, successful_notifications, available_dates, failed_requests = read_yesterday_execution_stats()

    if execution_times > 0:
        html_message = build_statistics_html_message(start_at, finish_at, execution_times, successful_notifications,
                                                     available_dates, failed_requests, new_users, missing_users)
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text="Support the project via credit card", url=SUPPORT_URL))
        keyboard.add(InlineKeyboardButton(text="Support the project via PayPal", url=PAYPAL_SUPPORT_URL))

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
