import os
import time
import sys
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

URL = "https://service.berlin.de/terminvereinbarung/termin/all/351180/"
CHECK_INTERVAL = 60

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=options)

def check_for_appointment():
    driver.get(URL)
    time.sleep(3)

    page_text = driver.page_source

    if "Leider sind aktuell keine Termine für ihre Auswahl verfügbar." in page_text:
        print("❌ No appointments yet...")
        return False
    elif "Forbidden access" in page_text:
        print("⚠️ Access denied. Check your settings or try again later.")
        return False
    else:
        print("✅ Looks like appointments have appeared!")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"index_{timestamp}.html"
        with open(filename, "w", encoding="utf-8") as file:
            file.write(page_text)
        return True

try:
    while True:
        print("Checking...", end="", flush=True)
        if check_for_appointment():
            os.system('say "There is available appointment!"')
            time.sleep(CHECK_INTERVAL+10)
            os.system(f"open {URL}")
            break

        for remaining in range(CHECK_INTERVAL, 0, -1):
            sys.stdout.write(f"\rNext check in {remaining} seconds...")
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write("\r" + " " * 50 + "\r")

finally:
    driver.quit()
