import os
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

import boto3
import humps
from aws_lambda_powertools import Logger, Tracer
from playwright.sync_api import sync_playwright

logger = Logger()
tracer = Tracer()
s3 = boto3.resource("s3")

S3_SHORT_TERM_BUCKET_NAME = os.getenv('S3_SHORT_TERM_BUCKET_NAME')


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
def lambda_handler(event, context):
    logger.debug("Received event", extra={"event": event})
    service_name = event.get("service_name")
    service_url = event.get("service_url")

    logger.debug(f"Load service page content by url: {service_url}")
    service_page_content = load_service_page_content(service_url)
    service_page_content_s3_key = get_service_page_content_s3_path(service_name)
    logger.debug(f"Put service page from {service_url} to s3://{S3_SHORT_TERM_BUCKET_NAME}/{service_page_content_s3_key}")
    store_service_page_content_to_s3(service_page_content_s3_key, service_page_content)
    return {
            "service_page_content_s3_key": service_page_content_s3_key,
            "service_page_content_s3_bucket": S3_SHORT_TERM_BUCKET_NAME, }


@tracer.capture_method
def load_service_page_content(service_url: str) -> str:
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
        page_content = page.content()
        browser.close()
    return page_content


@tracer.capture_method
def get_service_page_content_s3_path(service_name: str) -> str:
    now = datetime.now(timezone.utc)
    s3_key = f"{humps.kebabize(service_name)}/{now:%Y/%m/%d}/{now:%H%M%S}_{uuid4().hex}"
    return s3_key


@tracer.capture_method
def store_service_page_content_to_s3(service_page_content_s3_key: str, service_page_content: str, ):
    s3.Object(S3_SHORT_TERM_BUCKET_NAME, service_page_content_s3_key).put(Body=service_page_content.encode('utf-8'))
    logger.debug(f"Service page content has been stored to S3 with key: {service_page_content_s3_key}")


if __name__ == '__main__':
    class Context:
        function_name = "termin-radar-check-function"
        memory_limit_in_mb = 128
        invoked_function_arn = "arn:aws:lambda:eu-central-1:123456789012:function:termin-radar-check-function"
        aws_request_id = "test-request-id"


    lambda_handler({
            "service_name": "einbuergerungstest",
            "service_url": "https://service.berlin.de/terminvereinbarung/termin/all/351180/"}, Context())
