from playwright.sync_api import sync_playwright


def lambda_handler(event, context):
    url = event.get("url", "https://example.com")
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
    return {
            "url": url,
            "title": title,
            "length": len(html),
            "has_login_text": has_login,
            "html_snippet": html[:400]
            }
