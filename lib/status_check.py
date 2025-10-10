from lib.extract_dates import extract_available_dates
from lib.utils import save_html, get_html_page, CheckStatus


def check_for_appointment(url, postfix="", delay=0):
    page_text = get_html_page(url, delay)
    appointment_status = check_on_page(page_text, postfix)
    available_dates = []
    if appointment_status == CheckStatus.APPOINTMENTS_AVAILABLE:
        available_dates = extract_available_dates(page_text)
    return appointment_status, available_dates


def check_on_page(page_text, postfix=""):
    if "Bitte wählen Sie ein Datum" in page_text:
        print("✅ Looks like appointments have appeared!")
        return CheckStatus.APPOINTMENTS_AVAILABLE
    elif "Leider sind aktuell keine Termine für ihre Auswahl verfügbar." in page_text:
        print("❌ No appointments yet...")
        return CheckStatus.NO_APPOINTMENTS
    elif "Forbidden access" in page_text:
        print("⚠️ Access denied. Check your settings or try again later.")
        return CheckStatus.ACCESS_DENIED
    elif "Zu viele Zugriffe" in page_text:
        print("⚠️ Too many requests. Please wait before trying again.")
        return CheckStatus.TOO_MANY_REQUESTS
    elif "This site can’t be reached" in page_text:
        print("⚠️ The webpage might be temporarily down or it may have moved permanently to a new web address.")
        return CheckStatus.SITE_UNREACHABLE
    elif "Die Terminvereinbarung ist zur Zeit nicht" in page_text:
        print("⚠️ Maintenance for the base service Digital Application")
        return CheckStatus.MAINTENANCE
    elif "Bitte probieren Sie es zu einem späteren Zeitpunkt erneut." in page_text:
        print("⚠️ Please try again later.")
        return CheckStatus.TRY_AGAIN_LATER
    else:
        print("✅ Unknown page detected. Saving for analysis.")
        save_html(page_text, f"unknown_{postfix}")
        return CheckStatus.UNKNOWN_PAGE
