from enum import Enum

import boto3
from aws_lambda_powertools import Logger, Tracer

logger = Logger()
tracer = Tracer()

s3 = boto3.client("s3")

class CheckStatus(Enum):
    APPOINTMENTS_AVAILABLE = "Appointments Available"
    NO_APPOINTMENTS = "No Appointments"
    ACCESS_DENIED = "Access Denied"
    TOO_MANY_REQUESTS = "Too Many Requests"
    SITE_UNREACHABLE = "Site Unreachable"
    MAINTENANCE = "Maintenance"
    TRY_AGAIN_LATER = "Try Again Later"
    UNKNOWN_PAGE = "Unknown Page"


@logger.inject_lambda_context
@tracer.capture_lambda_handler
def service_berlin_de(event, context):
    logger.debug("Received event", extra={"event": event})
    service_name = event.get("service_name")
    service_page_content_s3_bucket = event.get("service_page_content_s3_bucket")
    service_page_content_s3_key = event.get("service_page_content_s3_key")

    response = s3.get_object(Bucket=service_page_content_s3_bucket, Key=service_page_content_s3_key)
    content = response['Body'].read().decode('utf-8')
    logger.debug(f"Read S3 object content for service {service_name}",
                 extra={
                         "path": f"s3://{service_page_content_s3_bucket}/{service_page_content_s3_key}",
                         "content_length": len(content)})

    return {"result": "OK", "status": get_status(content).value}


def get_status(content):
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
