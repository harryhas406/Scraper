# from playwright.sync_api import sync_playwright
# import json
# import time
# import random

# COOKIES_FILE = "darkforums_cookies_raw.json"
# OUTPUT_FILE = "darkforums_threads.json"

# def convert_chrome_cookies(raw_cookies):
#     converted = []
#     for c in raw_cookies:
#         # Map sameSite values to Playwright's accepted values
#         same_site = c.get("sameSite", "Lax")
#         if same_site.lower() in ["no_restriction", "none"]:
#             same_site = "None"
#         elif same_site.lower() == "lax":
#             same_site = "Lax"
#         elif same_site.lower() == "strict":
#             same_site = "Strict"
#         else: # handles "unspecified" and any unknown value
#             same_site = "Lax"  # default fallback

#         converted.append({
#             "name": c["name"],
#             "value": c["value"],
#             "domain": c["domain"],
#             "path": c.get("path", "/"),
#             "expires": int(c["expirationDate"]) if "expirationDate" in c else -1,
#             "httpOnly": c.get("httpOnly", False),
#             "secure": c.get("secure", False),
#             "sameSite": same_site
#         })
#     return converted

# def load_cookies(ctx):
#     with open(COOKIES_FILE, "r") as f:
#         raw = json.load(f)
#         cookies = convert_chrome_cookies(raw)
#         ctx.add_cookies(cookies)
#     print("✅ Cookies loaded")

# def scrape_darkforums():
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=True)
#         ctx = browser.new_context()
#         load_cookies(ctx)
#         page = ctx.new_page()

#         target_url = "https://darkforums.st/Forum-Databases"
#         print(f"🌐 Navigating to {target_url}")
#         page.goto(target_url, timeout=60000)

#         page.wait_for_selector("span.subject_new a", timeout=15000)
#         print("📦 Threads loaded")

#         thread_elements = page.locator("span.subject_new a")
#         count = thread_elements.count()
#         print(f"🔍 Found {count} threads")

#         threads = []

#         for i in range(count):
#             a_tag = thread_elements.nth(i)
#             title = a_tag.inner_text().strip()
#             relative_link = a_tag.get_attribute("href")
#             full_link = f"https://darkforums.st/{relative_link}" if relative_link else None
#             print(f"🧵 {title} → {full_link}")
#             threads.append({"title": title, "link": full_link})
#             time.sleep(random.uniform(2, 4))  # polite delay

#         with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
#             json.dump(threads, f, indent=2)

#         print(f"✅ Scraped data saved to {OUTPUT_FILE}")
#         browser.close()

# if __name__ == "__main__":
#     scrape_darkforums()
# This script scrapes thread titles and links from the DarkForums website using Playwright with cookies for authentication.
# It saves the scraped data to a JSON file.
# Ensure you have the necessary cookies in the `darkforums_cookies.json` file before running this script.

# -------------------------------------------------------------------------------------------------- #
# from playwright.sync_api import sync_playwright
# from playwright_stealth import stealth_sync # New (v2.0.0+)
# import json
# import time
# import random

# COOKIES_FILE = "darkforums_cookies_raw.json"
# OUTPUT_FILE = "darkforums_thread_data.json"

# def convert_chrome_cookies(raw_cookies):
#     converted = []
#     for c in raw_cookies:
#         same_site = c.get("sameSite", "Lax")
#         if same_site.lower() in ["no_restriction", "none"]:
#             same_site = "None"
#         elif same_site.lower() == "lax":
#             same_site = "Lax"
#         elif same_site.lower() == "strict":
#             same_site = "Strict"
#         else:
#             same_site = "Lax"

#         converted.append({
#             "name": c["name"],
#             "value": c["value"],
#             "domain": c["domain"],
#             "path": c.get("path", "/"),
#             "expires": int(c["expirationDate"]) if "expirationDate" in c else -1,
#             "httpOnly": c.get("httpOnly", False),
#             "secure": c.get("secure", False),
#             "sameSite": same_site
#         })
#     return converted

# def load_cookies(ctx):
#     with open(COOKIES_FILE, "r") as f:
#         raw = json.load(f)
#         cookies = convert_chrome_cookies(raw)
#         ctx.add_cookies(cookies)
#     print("✅ Cookies loaded")

# def scrape_darkforums():
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=False)
#         ctx = browser.new_context()
#         load_cookies(ctx)
#         page = ctx.new_page()
#         stealth_sync(page)  # New way (v2.0.0+)

#         main_url = "https://darkforums.st/Forum-Databases"
#         print(f"🌐 Navigating to {main_url}")
#         page.goto(main_url, timeout=60000)

#         page.wait_for_selector("span.subject_new a", timeout=120000)
#         print("📦 Threads loaded")

#         thread_elements = page.locator("span.subject_new a")
#         count = thread_elements.count()
#         print(f"🔍 Found {count} threads")

#         threads_data = []

#         for i in range(count):
#             a_tag = thread_elements.nth(i)
#             title = a_tag.inner_text().strip()
#             relative_link = a_tag.get_attribute("href")
#             full_link = f"https://darkforums.st/{relative_link}" if relative_link else None
#             print(f"➡️ Opening thread: {title} → {full_link}")

#             # Navigate to thread
#             try:
#                 page.goto(full_link, timeout=60000)
#                 page.wait_for_selector("div.post_body", timeout=15000)

#                 # Extract post content
#                 post_body = page.locator("div.post_body").nth(0).inner_text().strip()

#                 # Extract timestamp
#                 post_date = page.locator("span.post_date").nth(0).inner_text().strip()

#                 # Extract username + profile link
#                 user_element = page.locator("span.largetext a").nth(0)
#                 author_username = user_element.inner_text().strip()
#                 user_profile_link = "https://darkforums.st" + user_element.get_attribute("href")

#                 threads_data.append({
#                     "title": title,
#                     "link": full_link,
#                     "timestamp": post_date,
#                     "author": author_username,
#                     "profile_link": user_profile_link,
#                     "content": post_body
#                 })

#                 print(f"✅ Scraped → {title}")
#             except Exception as e:
#                 print(f"❌ Failed to scrape {full_link}: {e}")

#             time.sleep(random.uniform(6, 10))  # delay between threads

#         # Save to file
#         with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
#             json.dump(threads_data, f, indent=2, ensure_ascii=False)

#         print(f"📁 Results saved to {OUTPUT_FILE}")
#         browser.close()

# if __name__ == "__main__":
#     scrape_darkforums()

# ----------------------------------------------------------------------------------------------------- #
# Here is your updated full script using:
# ✅ Persistent browser context
# ✅ Login using pre-saved cookies
# ✅ Resilient handling of Cloudflare DDoS pages
# ✅ Waits for thread content (with fallback if DDoS stalls it)
# ✅ Saves to JSON
from playwright.sync_api import sync_playwright
from pathlib import Path
import json
import time
import random
import os

COOKIES_FILE = "darkforums_cookies_raw.json"
OUTPUT_FILE = "darkforums_thread_data.json"
USER_DATA_DIR = "./.pf_darkforums_user_data"  # persistent context
TARGET_URL = "https://darkforums.st/Forum-Databases"

# def convert_chrome_cookies(raw_cookies):
#     converted = []
#     for c in raw_cookies:
#         same_site = c.get("sameSite", "Lax")
#         same_site = (
#             "None" if same_site.lower() in ["no_restriction", "none"]
#             else "Lax" if same_site.lower() in ["lax", "unspecified"]
#             else "Strict"
#         )
#         converted.append({
#             "name": c["name"],
#             "value": c["value"],
#             "domain": c["domain"],
#             "path": c.get("path", "/"),
#             "expires": int(c["expirationDate"]) if "expirationDate" in c else -1,
#             "httpOnly": c.get("httpOnly", False),
#             "secure": c.get("secure", False),
#             "sameSite": same_site
#         })
#     return converted

# def load_cookies(context):
#     if not Path(COOKIES_FILE).exists():
#         print("❌ Cookies file not found.")
#         return
#     with open(COOKIES_FILE, "r") as f:
#         raw = json.load(f)
#         cookies = convert_chrome_cookies(raw)
#         context.add_cookies(cookies)
#         print("✅ Cookies loaded into context")

def scrape_darkforums():
    with sync_playwright() as p:
        print("🚀 Launching persistent browser...")
        browser = p.chromium.launch_persistent_context(
            USER_DATA_DIR,
            headless=False,
            viewport={"width": 1280, "height": 800}
        )
        # page = browser.new_page()
        page = browser.pages[0] if browser.pages else browser.new_page()
        print(f"🌐 Navigating to {TARGET_URL}")
        page.goto(TARGET_URL, timeout=60000)

        print("🟢 Waiting for threads to load...")
        page.wait_for_selector("span.subject_new a", timeout=120000)
        print("📦 Page passed DDoS and thread list is visible.")

        thread_elements = page.locator("span.subject_new a")
        count = thread_elements.count()
        print(f"🔍 Found {count} threads")

        threads = []
        threads_data = []
        TMP_FILE = "darkforums_threads_tmp.json"

        for i in range(count):
            try:
                a_tag = thread_elements.nth(i)
                title = a_tag.inner_text().strip()
                relative_link = a_tag.get_attribute("href")
                full_link = f"https://darkforums.st/{relative_link}" if relative_link else None

                print(f"➡️ Opening thread: {title} → {full_link}")
                page.goto(full_link, timeout=60000)
                page.wait_for_load_state("load")

                # Wait for DDoS or post body
                page.wait_for_selector("div.post_body, .cf-browser-verification", timeout=30000)

                if page.locator("div.post_body").count() == 0:
                    print("⏳ DDoS check detected, waiting longer...")
                    time.sleep(8)
                    page.wait_for_selector("div.post_body", timeout=30000)

                post_body = page.locator("div.post_body").nth(0).inner_text().strip()
                post_date = page.locator("span.post_date").nth(0).inner_text().strip()
                user_element = page.locator("span.largetext a").nth(0)
                author_username = user_element.inner_text().strip()
                user_profile_link = user_element.get_attribute("href")

                threads_data.append({
                    "title": title,
                    "link": full_link,
                    "timestamp": post_date,
                    "author": author_username,
                    "profile_link": user_profile_link,
                    "content": post_body
                })

                # Save progress to tmp file after each thread
                with open(TMP_FILE, "w", encoding="utf-8") as f:
                    json.dump(threads_data, f, indent=2, ensure_ascii=False)

                print(f"✅ Scraped → {title}")
                time.sleep(random.uniform(6, 10))  # delay between threads

            except Exception as e:
                print(f"❌ Failed to scrape thread: {e}")
                # Still save progress if an error occurs
                with open(TMP_FILE, "w", encoding="utf-8") as f:
                    json.dump(threads_data, f, indent=2, ensure_ascii=False)
                continue

        # Save to JSON file (append if file exists)
        if os.path.exists(OUTPUT_FILE):
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    existing_data = []
        else:
            existing_data = []

        # Avoid duplicates (based on thread link)
        existing_links = {item["link"] for item in existing_data}
        new_data = [item for item in threads_data if item["link"] not in existing_links]

        # Append and save
        all_data = existing_data + new_data
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)

        print(f"📁 Appended {len(new_data)} new threads to {OUTPUT_FILE} (Total: {len(all_data)})")

        browser.close()

if __name__ == "__main__":
    scrape_darkforums()

