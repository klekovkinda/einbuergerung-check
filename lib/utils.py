import os
import random
import time

import boto3
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


PROMOTION_MESSAGE = (
        f"Found a slot? Now prepare for the test!\n"
        f"Try this free, ad-free app for iPhone & Mac: https://apps.apple.com/app/id6745673617\n"
        "It includes in-line translations, explanations for the questions, and lets you take or review practice tests.\n")

def save_html(page_text, postfix):
    filename = f"output/html/index_{postfix}.html"
    folder_path = os.path.dirname(filename)
    os.makedirs(folder_path, exist_ok=True)
    with open(filename, "w", encoding="utf-8") as file:
        file.write(page_text)


def get_html_page(url, delay=3):
    user_agent = UserAgent()

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    options.add_argument(f"user-agent={user_agent}")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    with webdriver.Chrome(options=options) as driver:
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """})
        width = random.randint(800, 1920)
        height = random.randint(600, 1080)
        driver.set_window_size(width, height)
        driver.get(url)
        time.sleep(delay)
        page_text = driver.page_source
    return page_text

def get_dynamodb_table(name: str):
    dynamodb = boto3.resource("dynamodb")
    return dynamodb.Table(name)

def build_html_message(available_dates):
    return ("<b>Go and book your appointment now!</b>\n"
            "Available dates:\n") + "\n".join(f"• {available_date}" for available_date in available_dates)


def build_statistics_html_message(start_at: str = "00:00:00", finish_at: str = "00:00:00", execution_times: int = 0,
                                  successful_notifications: int = 0, available_dates: int = 0, failed_requests: int = 0,
                                  new_users: int = 0, missing_users: int = 0) -> str:
    # Execution times sentence
    if execution_times == 1:
        execution_times_msg = f"Between <strong>{start_at}</strong> and <strong>{finish_at}</strong>, I checked <strong>1</strong> time."
    else:
        execution_times_msg = f"Between <strong>{start_at}</strong> and <strong>{finish_at}</strong>, I checked <strong>{execution_times}</strong> times."

    # Successful notifications sentence
    if successful_notifications == 1 and available_dates == 1:
        successful_notifications_msg = (
            f"\nI managed to find an open slot and sent you <strong>1</strong> notification for <strong>1</strong> date!"
        )
    elif successful_notifications == 1:
        successful_notifications_msg = (
            f"\nI managed to find an open slot and sent you <strong>1</strong> notification for <strong>{available_dates}</strong> different dates!"
        )
    elif available_dates == 1 and successful_notifications > 1:
        successful_notifications_msg = (
            f"\nI managed to find open slots and sent you <strong>{successful_notifications}</strong> notifications for <strong>1</strong> date!"
        )
    elif successful_notifications > 0:
        successful_notifications_msg = (
            f"\nI managed to find open slots and sent you <strong>{successful_notifications}</strong> notifications for <strong>{available_dates}</strong> different dates!"
        )
    else:
        successful_notifications_msg = " "

    # Failed requests sentence
    if failed_requests == 1:
        failed_requests_msg = (
            "There was <strong>1</strong> time when I couldn’t load the info — sorry about that! "
            "But no worries, the team is working hard to improve the service every day."
        )
    else:
        failed_requests_msg = (
            f"There were <strong>{failed_requests}</strong> times when I couldn’t load the info — sorry about that! "
            "But no worries, the team is working hard to improve the service every day."
        )

    # New users sentence
    if new_users == 1:
        new_users_msg = (
            "\n🎉 We’ve got <strong>1</strong> new member in the channel — welcome aboard! "
            "Wishing you the best of luck finding a test slot 🍀 "
        )
    elif new_users > 1:
        new_users_msg = (
            f"\n🎉 We’ve got <strong>{new_users}</strong> new members in the channel — welcome aboard! "
            "Wishing you the best of luck finding a test slot 🍀 "
        )
    else:
        new_users_msg = " "

    # Missing users sentence
    if missing_users == 1:
        missing_users_msg = (
            "And a little shoutout to the <strong>1</strong> person who left the channel — we’re guessing she/he finally grabbed a slot! "
            "Let’s all wish her/him good luck on the test 🤞🇩🇪\n"
        )
    elif missing_users > 1:
        missing_users_msg = (
            f"And a little shoutout to the <strong>{missing_users}</strong> folks who left the channel — we’re guessing they finally grabbed a slot! "
            "Let’s all wish them good luck on the test 🤞🇩🇪\n"
        )
    else:
        missing_users_msg = ""

    return (
        f"\nHey friends!\n"
        "I'm <strong>Termin Radar 😎</strong> While you were waiting yesterday, I wasn’t just twiddling my thumbs — I was scanning like crazy for available Einbürgerungstest appointments!\n"
        f"{execution_times_msg} {successful_notifications_msg}\n"
        f"{failed_requests_msg}{new_users_msg}\n"
        f"{missing_users_msg}{PROMOTION_MESSAGE}\n"
        f"Like what I'm doing? You can support the project and help me keep scanning for you! 🙌\n"
    )
