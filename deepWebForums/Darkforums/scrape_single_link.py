from playwright.sync_api import sync_playwright
import os

PROFILE_DIR = os.path.abspath("darkforums-firefox-profile")
THREAD_URL = "https://darkforums.st/Thread-Selling-INDIA-1-7-MILLION-LIVPURE-PERSONAL-DATA-WITH-LOTS-OF-INFORMATION?highlight=livpure"

def scrape_single_thread():
    with sync_playwright() as p:
        context = p.firefox.launch_persistent_context(
            PROFILE_DIR,
            headless=False,
            args=["--start-maximized"]
        )
        page = context.pages[0] if context.pages else context.new_page()
        print(f"🌐 Navigating to {THREAD_URL}")
        page.goto(THREAD_URL, timeout=60000)
        try:
            page.wait_for_selector("div.post_body", timeout=15000)
            post_body = page.locator("div.post_body").first.inner_text().strip()
            print("\n--- Post Body ---\n")
            print(post_body)
        except Exception as e:
            print(f"❌ Could not find post body: {e}")
            print(page.content())
        context.close()

if __name__ == "__main__":
    scrape_single_thread()