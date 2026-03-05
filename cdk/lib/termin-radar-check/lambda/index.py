from aws_lambda_powertools import Logger, Tracer
from playwright.sync_api import sync_playwright

logger = Logger()
tracer = Tracer()

@tracer.capture_lambda_handler
def lambda_handler(event, context):
    logger.debug("Received event", extra={"event": event})
    url = event.get("url", "https://example.com")
    title, html, has_login = load_page_content(url)
    return {"url": url, "title": title, "length": len(html), "has_login_text": has_login, "html_snippet": html[:400]}

@tracer.capture_method
def load_page_content(url: str):
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
                                     args=["--no-sandbox",
                                           "--disable-gpu",
                                           "--single-process",
                                           "--disable-dev-shm-usage",
                                           "--disable-setuid-sandbox",
                                           "--disable-dev-shm-usage", ])
        page = browser.new_page()
        page.goto(url, wait_until="load", timeout=10000)
        title = page.title()
        html = page.content()
        has_login = page.locator("text=Login, text=Sign in").first.is_visible() if page.locator(
                "text=Login, text=Sign in").count() > 0 else False
        browser.close()
        return title, html, has_login
