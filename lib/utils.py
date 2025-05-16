import os
import random
import time

from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


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


def build_html_message(available_dates):
    return ("<b>Go and book your appointment now!</b>\n"
            "Available dates:\n") + "\n".join(f"• {available_date}" for available_date in available_dates)


def build_statistics_html_message(start_at: str = "00:00:00", finish_at: str = "00:00:00", execution_times: int = 0,
                                  successful_notifications: int = 0, available_dates: int = 0, failed_requests: int = 0,
                                  new_users: int = 0, missing_users: int = 0) -> str:
    successful_notifications_msg = f"""
I managed to find open slots and sent you <strong>{successful_notifications}</strong> notifications for <strong>{available_dates}</strong> different dates!""" if successful_notifications != 0 else " "
    new_users_msg = f"""
🎉 We’ve got <strong>{new_users}</strong> new members in the channel — welcome aboard! Wishing you the best of luck finding a test slot 🍀 """ if new_users != 0 else " "
    missing_users_msg = f"""And a little shoutout to the <strong>{missing_users}</strong> folks who left the channel — we’re guessing they finally grabbed a slot! Let’s all wish them good luck on the test 🤞🇩🇪
""" if missing_users != 0 else " "
    return (f"""
Hey friends!
I'm <strong>Termin Radar 😎</strong> While you were waiting yesterday, I wasn’t just twiddling my thumbs — I was scanning like crazy for available Einbürgerungstest appointments!
Between <strong>{start_at}</strong> and <strong>{finish_at}</strong>, I checked <strong>{execution_times}</strong> times. {successful_notifications_msg}
There were <strong>{failed_requests}</strong> times when I couldn’t load the info — sorry about that! But no worries, the team is working hard to improve the service every day.{new_users_msg}
{missing_users_msg}Like what I'm doing? You can support the project and help me keep scanning for you! 🙌
""")
