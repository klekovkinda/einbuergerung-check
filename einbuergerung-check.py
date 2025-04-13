import os
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

URL = "https://service.berlin.de/terminvereinbarung/termin/all/351180/"
CHECK_INTERVAL = 120
DELTA_INTERVAL = 5

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=options)

def check_for_appointment():
    driver.get(URL)
    time.sleep(DELTA_INTERVAL)

    page_text = driver.page_source

    if "Leider sind aktuell keine Termine für ihre Auswahl verfügbar." in page_text:
        print("❌ No appointments yet...")
        return False
    elif "Forbidden access" in page_text:
        print("⚠️ Access denied. Check your settings or try again later.")
        return False
    elif "Zu viele Zugriffe" in page_text:
        print("⚠️ Too many requests. Please wait before trying again.")
        return False
    else:
        print("✅ Looks like appointments have appeared!")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("html", exist_ok=True)
        filename = f"html/index_{timestamp}.html"
        with open(filename, "w", encoding="utf-8") as file:
            file.write(page_text)
        return True


try:
    while True:
        print("Checking...", end="", flush=True)
        if check_for_appointment():
            break
        time.sleep(CHECK_INTERVAL)

finally:
    driver.quit()
