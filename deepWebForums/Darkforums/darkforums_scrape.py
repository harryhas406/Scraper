from playwright.sync_api import sync_playwright
import json
import os
import time
import random
from urllib.parse import urlparse

PROFILE_DIR = os.path.abspath("darkforums-firefox-profile")
LISTING_URL = "https://darkforums.st/Forum-Leaks-Market"  # <-- Change to your forum section URL
THREADS_FILE = "threads_tmp.json"
OUTPUT_FILE = "darkforums_single_link_threads.json"

def get_forum_section(url):
    parsed = urlparse(url)
    return parsed.path.lstrip("/")

def collect_thread_links():
    with sync_playwright() as p:
        context = p.firefox.launch_persistent_context(
            PROFILE_DIR,
            headless=False,
            args=["--start-maximized"]
        )
        page = context.pages[0] if context.pages else context.new_page()
        print(f"🌐 Navigating to {LISTING_URL}")
        page.goto(LISTING_URL, timeout=120000)

        print("🟢 Waiting for threads to load...")
        page.wait_for_selector("span.subject_new a", timeout=120000)
        print("📦 Page passed DDoS and thread list is visible.")

        thread_elements = page.locator("span.subject_new a")
        count = thread_elements.count()
        print(f"🔍 Found {count} threads")

        threads = []
        for i in range(count):
            a_tag = thread_elements.nth(i)
            title = a_tag.inner_text().strip()
            link = a_tag.get_attribute("href")
            if link and not link.startswith("http"):
                link = "https://darkforums.st/" + link.lstrip("/")
            threads.append({"title": title, "link": link})

        with open(THREADS_FILE, "w", encoding="utf-8") as f:
            json.dump(threads, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved {len(threads)} threads to {THREADS_FILE}")

        context.close()

def scrape_threads_from_file():
    with open(THREADS_FILE, "r", encoding="utf-8") as f:
        threads = json.load(f)

    # Load existing scraped threads if the file exists
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            scraped = json.load(f)
    else:
        scraped = []
    print(f"🔄 Loaded {len(scraped)} previously scraped threads from {OUTPUT_FILE}")
    print(f"🔍 Starting to scrape {len(threads)} threads from {LISTING_URL}")
    
    # Extract forum section from the listing URL
    forum_section = get_forum_section(LISTING_URL)
    
    with sync_playwright() as p:
        context = p.firefox.launch_persistent_context(
            PROFILE_DIR,
            headless=False,
            args=["--start-maximized"]
        )
        page = context.pages[0] if context.pages else context.new_page()

        for idx, thread in enumerate(threads):
            link = thread["link"]
            title = thread["title"]
            print(f"\n➡️ [{idx+1}/{len(threads)}] Scraping: {title} → {link}")
            try:
                page.goto(link, timeout=120000)
                page.wait_for_load_state("domcontentloaded")
                # Wait for post body or login warning
                try:
                    page.wait_for_selector("div.post_body", timeout=15000)
                    post_body = page.locator("div.post_body").first.inner_text().strip()
                    # post_date = page.locator("span.post_date").nth(0).inner_text().strip()
                    date_elem = page.locator("span.post_date").first
                    # Try to get the inner <span> with a title attribute
                    title_attr = date_elem.locator("span[title]").get_attribute("title")
                    if title_attr:
                        post_date = title_attr.strip()
                    else:
                        post_date = date_elem.inner_text().strip()
                    user_element = page.locator("span.largetext a").nth(0)
                    author_username = user_element.inner_text().strip()
                    user_profile_link = user_element.get_attribute("href")
                except:
                    post_body = "[Failed to load post body or not visible]"

                scraped.append({
                    # "original_index": idx,
                    "forum_section": forum_section,  # Adjust as needed
                    "forum_url": LISTING_URL,
                    "forum_name": "DarkForums",
                    "title": title,
                    "link": link,
                    "timestamp": post_date,
                    "author": author_username,
                    "profile_link": user_profile_link,
                    "content": post_body
                })

                # Save progress after each thread
                with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                    json.dump(scraped, f, indent=2, ensure_ascii=False)

                print(f"✅ Scraped: {title}")
                # Human-like delay and scroll
                delay = random.uniform(7, 15)
                print(f"⏳ Waiting {delay:.1f} seconds before next thread...")
                time.sleep(delay)
                scroll_amount = random.randint(300, 1200)
                page.mouse.wheel(0, scroll_amount)
                print(f"🖱️ Scrolled down {scroll_amount} pixels.")
            except Exception as e:
                print(f"❌ Error scraping {title}: {e}")
                continue

        context.close()
    print(f"\n🎉 Done! Scraped {len(scraped)} threads. Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    # Step 1: Collect thread links (run once, or when you want to refresh the thread list)
    collect_thread_links()
    # Step 2: Scrape threads from the saved file
    scrape_threads_from_file()