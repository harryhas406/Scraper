from playwright.sync_api import sync_playwright
import os
import json

PROFILE_DIR = os.path.abspath("darkforums-firefox-profile")
THREAD_URL = "https://darkforums.st/Thread-Chaoxin-Xuexitong-2022-140M-Leak"
OUTPUT_FILE = "single_thread.json"

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
            # Get post date (handle both formats)
            post_date = "[not found]"
            try:
                page.wait_for_selector("span.post_date", timeout=15000)
                date_elem = page.locator("span.post_date").first

                # Check if a nested span[title] exists
                nested_title_spans = date_elem.locator("span[title]")
                if nested_title_spans.count() > 0:
                    title_attr = nested_title_spans.first.get_attribute("title")
                    post_date = title_attr.strip() if title_attr else "[not found]"
                else:
                    post_date = date_elem.inner_text().strip()
            except Exception as e:
                    print(f"⚠️ Could not extract post date: {e}")
            post_body = page.locator("div.post_body").first.inner_text().strip()
            result = {
                "url": THREAD_URL,
                "timestamp": post_date,
                "author_username": page.locator("span.largetext a").nth(0).inner_text().strip(),
                "user_profile_link": page.locator("span.largetext a").nth(0).get_attribute("href"),
                "content": post_body
            }
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"✅ Post body saved to {OUTPUT_FILE}")
        except Exception as e:
            print(f"❌ Could not find post body: {e}")
            print(page.content())
        context.close()

if __name__ == "__main__":
    scrape_single_thread()