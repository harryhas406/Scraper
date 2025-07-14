# bhw_login_playwright.py
from playwright.sync_api import sync_playwright
import json
import os

COOKIES_FILE = "bhw_cookies.json"
PROFILE_DIR = os.path.abspath("bhw-firefox-profile")

def manual_login_and_save_cookies():
    with sync_playwright() as p:
        # Launch Firefox with a persistent profile
        context = p.firefox.launch_persistent_context(
            PROFILE_DIR,
            headless=False,
            args=["--start-maximized"]
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://www.blackhatworld.com", timeout=60000)
        print("🌐 Please log in manually and solve any CAPTCHA if present.")
        input("🔑 Press Enter here after you are fully logged in and see the forum...")

        # Save cookies
        cookies = context.cookies()
        with open(COOKIES_FILE, "w") as f:
            json.dump(cookies, f)
        print(f"🗄️ Cookies saved to {COOKIES_FILE}")

        context.close()

if __name__ == "__main__":
    manual_login_and_save_cookies()
