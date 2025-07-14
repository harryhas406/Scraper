# bhw_scrape_playwright.py
from playwright.sync_api import sync_playwright
import json

COOKIES_FILE = "bhw_cookies.json"

def convert_firefox_cookies(raw_cookies):
    converted = []
    for c in raw_cookies:
        converted.append({
            "name": c.get("Name raw"),
            "value": c.get("Content raw"),
            "domain": "www.blackhatworld.com",
            "path": c.get("Path raw", "/"),
            "expires": -1 if c.get("Expires") == "At the end of the session" else int(c.get("Expires raw", "0")),
            "httpOnly": c.get("HTTP only raw", "false") == "true",
            "secure": c.get("Send for", "").lower().startswith("encrypted"),
            "sameSite": "None" if c.get("SameSite raw", "no_restriction").lower() == "no_restriction" else c.get("SameSite raw", "Lax").capitalize()
        })
    return converted

def load_cookies(ctx):
    with open(COOKIES_FILE) as f:
        raw_cookies = json.load(f)
        cookies = convert_firefox_cookies(raw_cookies)
        ctx.add_cookies(cookies)
    print("🔄 Cookies loaded from file")

def scrape_with_cookies():
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        ctx = browser.new_context()
        load_cookies(ctx)
        page = ctx.new_page()

        target_url = "https://www.blackhatworld.com/forums/seo-link-building.43/"
        print(f"🌐 Navigating to {target_url}")
        page.goto(target_url, timeout=60000)

        page.wait_for_selector("div.structItem-title", timeout=15000)
        print("📦 Found restricted content")

        items = page.locator("div.structItem-title")
        count = items.count()
        print(f"Total posts found: {count}")
        for i in range(count):
            post = items.nth(i)
            title = post.locator("a").inner_text().strip()
            link = post.locator("a").get_attribute("href")
            print(f"- {title} → {link}")

        browser.close()

if __name__ == "__main__":
    scrape_with_cookies()
