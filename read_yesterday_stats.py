import os
from datetime import datetime, timedelta, timezone

import boto3
import pytz
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from lib.status_check import CheckStatus
from lib.utils import build_statistics_html_message

SUPPORT_URL = "https://buymeacoffee.com/termin_radar"
PAYPAL_SUPPORT_URL = "https://www.paypal.com/pool/9f1bWcE4aK?sr=wccr"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
dynamodb = boto3.resource("dynamodb")


def get_users_for_date(date) -> set[str]:
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
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    start_at = f"{yesterday} 00:00:00"
    finish_at = f"{yesterday} 00:00:00"

    table = dynamodb.Table("termin_statistic")
    response = table.query(KeyConditionExpression=boto3.dynamodb.conditions.Key("execution_date").eq(yesterday))
    items = response.get("Items", [])

    start_at = min(item["execution_time"] for item in items if "execution_time" in item) if items else start_at
    finish_at = max(item["execution_time"] for item in items if "execution_time" in item) if items else finish_at

    execution_times_count = len(set(item["execution_time"] for item in items if "execution_time" in item))

    successful_notifications_count = len(set(
            item["execution_time"] for item in items if item.get("status") == CheckStatus.APPOINTMENTS_AVAILABLE.value))

    available_dates_count = len(set(item["appointment_date"] for item in items if
                                    item.get("appointment_date") and item.get("status") == CheckStatus.APPOINTMENTS_AVAILABLE.value))

    failed_requests_count = len(set(item["execution_time"] for item in items if
                                    item.get("status") not in [CheckStatus.APPOINTMENTS_AVAILABLE.value,
                                                               CheckStatus.NO_APPOINTMENTS.value,
                                                               CheckStatus.MAINTENANCE.value]))

    start_at_utc_time = datetime.strptime(start_at, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
    finish_at_utc_time = datetime.strptime(finish_at, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)

    return (start_at_utc_time.astimezone(pytz.timezone('Europe/Berlin')).strftime('%H:%M:%S'),
            finish_at_utc_time.astimezone(pytz.timezone('Europe/Berlin')).strftime('%H:%M:%S'),
            execution_times_count,
            successful_notifications_count,
            available_dates_count,
            failed_requests_count)


if __name__ == "__main__":
    new_users, missing_users = read_yesterday_user_stats()
    start_at, finish_at, execution_times, successful_notifications, available_dates, failed_requests = read_yesterday_execution_stats()

    if execution_times > 0:
        html_message = build_statistics_html_message(start_at,
                                                     finish_at,
                                                     execution_times,
                                                     successful_notifications,
                                                     available_dates,
                                                     failed_requests,
                                                     new_users,
                                                     missing_users)
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
