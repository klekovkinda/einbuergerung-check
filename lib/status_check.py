from lib.extract_dates import extract_available_dates
from lib.utils import save_html, get_html_page


def check_for_appointment(url, delay=0, saving_for_analysis=False):
    page_text = get_html_page(url, delay)
    appointment_available = check_on_page(page_text, saving_for_analysis)
    available_dates = []
    if appointment_available:
        available_dates = extract_available_dates(page_text)
    return appointment_available, available_dates


def check_on_page(page_text, saving_for_analysis=False):
    if "Bitte wählen Sie ein Datum" in page_text:
        print("✅ Looks like appointments have appeared!")
        if saving_for_analysis:
            save_html(page_text)
        return True
    elif "Leider sind aktuell keine Termine für ihre Auswahl verfügbar." in page_text:
        print("❌ No appointments yet...")
        return False
    elif "Forbidden access" in page_text:
        print("⚠️ Access denied. Check your settings or try again later.")
        return False
    elif "Zu viele Zugriffe" in page_text:
        print("⚠️ Too many requests. Please wait before trying again.")
        return False
    elif "This site can’t be reached" in page_text:
        print("⚠️ The webpage might be temporarily down or it may have moved permanently to a new web address.")
        return False
    elif "Bitte probieren Sie es zu einem späteren Zeitpunkt erneut." in page_text:
        print("⚠️ Please try again later.")
        return False
    else:
        print("✅ Unknown page detected. Saving for analysis.")
        save_html(page_text)
        return False
