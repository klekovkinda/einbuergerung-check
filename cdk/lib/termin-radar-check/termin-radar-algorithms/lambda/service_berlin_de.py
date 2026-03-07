import boto3
from aws_lambda_powertools import Logger
from bs4 import BeautifulSoup

from utils import AlgorithmParseResult, CheckStatus

logger = Logger()
s3 = boto3.client("s3")


def service_berlin_de_parce(service_page_content_s3_bucket: str, service_page_content_s3_key: str, service_name: str) -> AlgorithmParseResult:
    raw_data = s3.get_object(Bucket=service_page_content_s3_bucket, Key=service_page_content_s3_key)
    content = raw_data['Body'].read().decode('utf-8')
    logger.debug(f"Read S3 object content for service {service_name}",
                 extra={
                         "path": f"s3://{service_page_content_s3_bucket}/{service_page_content_s3_key}",
                         "content_length": len(content)})

    appointment_status = get_status(content)
    available_dates = []
    telegram_html_message = ""

    if appointment_status == CheckStatus.APPOINTMENTS_AVAILABLE:
        available_dates = extract_available_dates(content)
        telegram_html_message = build_html_message(available_dates)

    return AlgorithmParseResult(appointment_status=appointment_status,
                                available_dates=available_dates,
                                telegram_html_message=telegram_html_message)


def extract_available_dates(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    available_dates = []
    for cell in soup.find_all('td', class_='buchbar'):
        link = cell.find('a')
        if link:
            title = link.get('title', '')
            href = link.get('href', '')
            if title and href:
                available_dates.append(title.split(' ')[0])
    return available_dates


def build_html_message(available_dates):
    return ("<b>Go and book your appointment now!</b>\n"
            "Available dates:\n") + "\n".join(f"• {available_date}" for available_date in available_dates)


def get_status(content) -> CheckStatus:
    if "Bitte wählen Sie ein Datum" in content:
        logger.info("✅ Looks like appointments have appeared!")
        return CheckStatus.APPOINTMENTS_AVAILABLE
    elif "Leider sind aktuell keine Termine für ihre Auswahl verfügbar." in content:
        logger.warning("❌ No appointments yet...")
        return CheckStatus.NO_APPOINTMENTS
    elif "Forbidden access" in content:
        logger.warning("⚠️ Access denied. Check your settings or try again later.")
        return CheckStatus.ACCESS_DENIED
    elif "Zu viele Zugriffe" in content:
        logger.warning("⚠️ Too many requests. Please wait before trying again.")
        return CheckStatus.TOO_MANY_REQUESTS
    elif "This site can’t be reached" in content:
        logger.warning("⚠️ The webpage might be temporarily down or it may have moved permanently to a new web address.")
        return CheckStatus.SITE_UNREACHABLE
    elif "Die Terminvereinbarung ist zur Zeit nicht" in content:
        logger.warning("⚠️ Maintenance for the base service Digital Application")
        return CheckStatus.MAINTENANCE
    elif "Bitte probieren Sie es zu einem späteren Zeitpunkt erneut." in content:
        logger.warning("⚠️ Please try again later.")
        return CheckStatus.TRY_AGAIN_LATER
    else:
        logger.warning("✅ Unknown page detected. Saving for analysis.")
        logger.warning(content)
        return CheckStatus.UNKNOWN_PAGE
