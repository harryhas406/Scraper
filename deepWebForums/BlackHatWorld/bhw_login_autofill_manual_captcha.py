from playwright.sync_api import sync_playwright
import os

PROFILE_DIR = os.path.abspath("bhw-user-data-firefox")

def open_persistent_browser():
    with sync_playwright() as p:
        context = p.firefox.launch_persistent_context(
            PROFILE_DIR,
            headless=False,
            args=["--start-maximized"]
        )

        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://www.blackhatworld.com/")
        print("🌐 Browser opened to BHW")
        print("🧑‍💻 Please log in and solve the CAPTCHA manually.")
        print("❗ When you're done, just close the browser window.")
        input("🔑 Press Enter here after closing the browser window...")

        print("✅ Saving login session...")
        context.storage_state(path="bhw_logged_in_state.json")
        print("💾 Cookies saved to bhw_logged_in_state.json")
        context.close()

if __name__ == "__main__":
    open_persistent_browser()
