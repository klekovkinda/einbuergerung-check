import os
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def save_html(page_text):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("html", exist_ok=True)
    filename = f"html/index_{timestamp}.html"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(page_text)

def get_html_page(url, delay=3):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    # Use a context manager to ensure the WebDriver is properly closed
    with webdriver.Chrome(options=options) as driver:
        driver.get(url)
        time.sleep(delay)
        page_text = driver.page_source

    return page_text

