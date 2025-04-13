from lib.status_check import check_for_appointment

URL = "https://service.berlin.de/terminvereinbarung/termin/all/351180/"

print("Checking...", end="", flush=True)
if check_for_appointment(URL):
    print("Telegram bot notification sent.")
