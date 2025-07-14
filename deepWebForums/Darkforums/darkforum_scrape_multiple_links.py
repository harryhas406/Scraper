from playwright.sync_api import sync_playwright
import json
import os
import time
import random
from urllib.parse import urlparse
from datetime import datetime, timezone

PROFILE_DIR = os.path.abspath("darkforums-firefox-profile")
LISTING_URLS = [
    "https://darkforums.st/Forum-Databases",
    "https://darkforums.st/Forum-Leaks-Market",
    "https://darkforums.st/Forum-Leads-Market",
    "https://darkforums.st/Forum-Access-Market",
    "https://darkforums.st/Forum-Stealer-Logs",
    "https://darkforums.st/Forum-Combolists",
    "https://darkforums.st/Forum-Cracked-Accounts",
    "https://darkforums.st/Forum-Other-Leaks",
    "https://darkforums.st/Forum-Premium-Marketplace"
]
THREADS_FILE = "threads_tmp.json"
OUTPUT_FILE = "darkforums_threads.json"

def get_forum_section(url):
    parsed = urlparse(url)
    return parsed.path.lstrip("/")

def collect_thread_links(listing_urls):
    threads = []
    with sync_playwright() as p:
        context = p.firefox.launch_persistent_context(
            PROFILE_DIR,
            headless=False,
            args=["--start-maximized"]
        )
        page = context.pages[0] if context.pages else context.new_page()
        for listing_url in listing_urls:
            print(f"🌐 Navigating to {listing_url}")
            page.goto(listing_url, timeout=120000)
            print("🟢 Waiting for threads to load...")
            page.wait_for_selector('span[class*="subject_new"] a, span[class*="subject_old"] a', timeout=120000)
            print("📦 Page passed DDoS and thread list is visible.")

            thread_elements = page.locator('span[class*="subject_new"] a, span[class*="subject_old"] a')
            count = thread_elements.count()
            print(f"🔍 Found {count} threads")

            forum_section = get_forum_section(listing_url)
            for i in range(count):
                a_tag = thread_elements.nth(i)
                title = a_tag.inner_text().strip()
                link = a_tag.get_attribute("href")
                if link and not link.startswith("http"):
                    link = "https://darkforums.st/" + link.lstrip("/")
                threads.append({
                    "forum_section": forum_section,
                    "forum_url": listing_url,
                    "forum_name": "DarkForums",
                    "title": title,
                    "link": link
                })

        with open(THREADS_FILE, "w", encoding="utf-8") as f:
            json.dump(threads, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved {len(threads)} threads to {THREADS_FILE}")
        context.close()

def scrape_threads_from_file():
    with open(THREADS_FILE, "r", encoding="utf-8") as f:
        threads = json.load(f)

    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            scraped = json.load(f)
    else:
        scraped = []
    print(f"🔄 Loaded {len(scraped)} previously scraped threads from {OUTPUT_FILE}")

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

            if any(t["link"] == link for t in scraped):
                print("🔁 Already scraped, skipping.")
                continue

            try:
                page.goto(link, timeout=120000)
                page.wait_for_load_state("domcontentloaded")
                # Wait for post body or login warning
                try:
                    page.wait_for_selector("div.post_body", timeout=15000)
                    post_body = page.locator("div.post_body").first.inner_text().strip()
                    # post_date = page.locator("span.post_date").nth(0).inner_text().strip()
                    # Get post date (handle both formats)
                    post_date = "[not found]"
                    try:
                        page.wait_for_selector("span.post_date", timeout=15000)
                        date_elem = page.locator("span.post_date").first

                        # Check if a nested span[title] exists
                        # and extract the title attribute if available
                        # If not, fallback to the inner text
                        # This handles cases where the date is in a <span title="...">
                        # or just plain text
                        # Example: <span class="post_date"><span title="2023-10-01 12:34">October 1, 2023</span></span>
                        # or <span class="post_date">October 1, 2023</span>
                        # or <span class="post_date"><span title="2023-10-01 12:34">2023-10-01 12:34</span></span>
                        # or <span class="post_date">2023-10-01 12:34</span>
                        # or <span class="post_date"><span title="26-06-25">Yesterday</span>, 12:51 AM <span class="post_edit" id="edited_by_88783"></span></span>
                        nested_title_spans = date_elem.locator("span[title]")
                        if nested_title_spans.count() > 0:
                            title_attr = nested_title_spans.first.get_attribute("title")
                            post_date = title_attr.strip() if title_attr else "[not found]"
                        else:
                            post_date = date_elem.inner_text().strip()
                    except Exception as e:
                        print(f"⚠️ Could not extract post date: {e}")
                    # Get author and profile link
                    user_element = page.locator("span.largetext a").first
                    author_username = user_element.inner_text().strip()
                    user_profile_link = user_element.get_attribute("href")
                except:
                    post_body = "[Failed to load post body or not visible]"

                scraped.append({
                    "forum_section": thread["forum_section"],
                    "forum_url": thread["forum_url"],
                    "forum_name": thread["forum_name"],
                    "title": title,
                    "link": link,
                    "timestamp": post_date,
                    "scraped_at": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
                    "author": author_username,
                    "profile_link": user_profile_link,
                    "content": post_body
                })

                with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                    json.dump(scraped, f, indent=2, ensure_ascii=False)

                print(f"✅ Scraped: {title}")

                delay = random.uniform(7, 12)
                print(f"⏳ Waiting {delay:.1f} seconds before next thread...")
                time.sleep(delay)
                scroll_amount = random.randint(400, 1300)
                page.mouse.wheel(0, scroll_amount)
                print(f"🖱️ Scrolled down {scroll_amount} pixels.")

            except Exception as e:
                print(f"❌ Error scraping {title}: {e}")
                continue

        context.close()
    print(f"\n🎉 Done! Scraped {len(scraped)} threads. Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    collect_thread_links(LISTING_URLS)
    scrape_threads_from_file()