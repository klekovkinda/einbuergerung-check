import os
import random
import time
from datetime import datetime

from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def save_html(page_text):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("html", exist_ok=True)
    filename = f"html/index_{timestamp}.html"
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


def build_html_message(URL, available_dates):
    return ("<b>Go and book your appointment now!</b>\n"
            f"<a href='{URL}'>Click here to book the appointment</a>\n"
            "Available dates:\n") + "\n".join(f"• {available_date}" for available_date in available_dates)
