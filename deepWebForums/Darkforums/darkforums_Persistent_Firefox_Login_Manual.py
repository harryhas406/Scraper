from playwright.sync_api import sync_playwright
import os

PROFILE_DIR = os.path.abspath("darkforums-firefox-profile")

with sync_playwright() as p:
    context = p.firefox.launch_persistent_context(
        PROFILE_DIR,
        headless=False,
        args=["--start-maximized"]
    )
    page = context.pages[0] if context.pages else context.new_page()
    page.goto("https://darkforums.st/", timeout=60000)
    input("Log in manually, then press Enter here to close...")
    context.close()