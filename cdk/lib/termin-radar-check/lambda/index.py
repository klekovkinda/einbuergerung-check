import os
from enum import Enum

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.parameters import SSMProvider
from playwright.sync_api import sync_playwright

logger = Logger()
tracer = Tracer()

PROPERTY_PREFIX = os.getenv('PROPERTY_PREFIX')


class CheckStatus(Enum):
    APPOINTMENTS_AVAILABLE = "Appointments Available"
    NO_APPOINTMENTS = "No Appointments"
    ACCESS_DENIED = "Access Denied"
    TOO_MANY_REQUESTS = "Too Many Requests"
    SITE_UNREACHABLE = "Site Unreachable"
    MAINTENANCE = "Maintenance"
    TRY_AGAIN_LATER = "Try Again Later"
    UNKNOWN_PAGE = "Unknown Page"


@tracer.capture_lambda_handler
def lambda_handler(event, context):
    logger.debug("Received event", extra={"event": event})
    service_name = event.get("service_name")
    provider = SSMProvider()
    service_url = provider.get(f"/{PROPERTY_PREFIX}/{service_name}/service_url", decrypt=False)

    available_dates = find_available_dates(service_url)
    return {"service_url": service_url, "service_name": service_name, "available_dates": available_dates}


@tracer.capture_method
def find_available_dates(service_url: str):
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
                                     args=["--no-sandbox",
                                           "--disable-gpu",
                                           "--single-process",
                                           "--disable-dev-shm-usage",
                                           "--disable-setuid-sandbox",
                                           "--disable-dev-shm-usage", ])
        page = browser.new_page()
        page.goto(service_url, wait_until="load", timeout=10000)

        page_status = check_page(page)

        available_dates = []
        if page_status == CheckStatus.APPOINTMENTS_AVAILABLE:
            links = page.query_selector_all('td.buchbar a')
            for link in links:
                title = link.get_attribute('title')
                if title:
                    available_dates.append(title.split(' ')[0])
        browser.close()
        return available_dates


@tracer.capture_method
def check_page(page):
    if page.get_by_text("Bitte wählen Sie ein Datum").is_visible():
        logger.info("✅ Looks like appointments have appeared!")
        return CheckStatus.APPOINTMENTS_AVAILABLE
    elif page.get_by_text("Leider sind aktuell keine Termine für ihre Auswahl verfügbar.").is_visible():
        logger.warning("❌ No appointments yet...")
        return CheckStatus.NO_APPOINTMENTS
    elif page.get_by_text("Forbidden access").is_visible():
        logger.warning("⚠️ Access denied. Check your settings or try again later.")
        return CheckStatus.ACCESS_DENIED
    elif page.get_by_text("Zu viele Zugriffe").is_visible():
        logger.warning("⚠️ Too many requests. Please wait before trying again.")
        return CheckStatus.TOO_MANY_REQUESTS
    elif page.get_by_text("This site can’t be reached").is_visible():
        logger.warning("⚠️ The webpage might be temporarily down or it may have moved permanently to a new web address.")
        return CheckStatus.SITE_UNREACHABLE
    elif page.get_by_text("Die Terminvereinbarung ist zur Zeit nicht").is_visible():
        logger.warning("⚠️ Maintenance for the base service Digital Application")
        return CheckStatus.MAINTENANCE
    elif page.get_by_text("Bitte probieren Sie es zu einem späteren Zeitpunkt erneut.").is_visible():
        logger.warning("⚠️ Please try again later.")
        return CheckStatus.TRY_AGAIN_LATER
    else:
        logger.warning("✅ Unknown page detected. Saving for analysis.")
        logger.warning(page.content())
        return CheckStatus.UNKNOWN_PAGE


if __name__ == '__main__':
    lambda_handler({"service_name": "EinbuergerungtestTerminRadar"}, None)
