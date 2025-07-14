from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc
import time
import random
import json
import logging
import os
from datetime import datetime, timedelta
import re

# Configure logging
logging.basicConfig(
    filename="scraper.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Configure Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_service = Service("/home/cdot/Downloads/chromedriver-linux64 (v130)/chromedriver-linux64/chromedriver")  # Replace with the path to your chromedriver
driver = uc.Chrome(headless=True)

# Login URL and credentials
login_url = "https://darkforums.st/member.php?action=login"
login_username = "harry_has"  # Replace with your username
login_password = "ZXCvbnm0"  # Replace with your password

# Forum URLs to scrape
forum_urls = [
    "https://darkforums.st/Forum-Databases?page={}&sortby=started&order=desc&datecut=9999&prefix=0",
    "https://darkforums.st/Forum-Other-Leaks?page={}&sortby=started&order=desc&datecut=9999&prefix=0",
    "https://darkforums.st/Forum-Stealer-Logs?page={}&sortby=started&order=desc&datecut=9999&prefix=0",
    "https://darkforums.st/Forum-Cracked-Accounts?page={}&sortby=started&order=desc&datecut=9999&prefix=0",
    "https://darkforums.st/Forum-Combolists?page={}&sortby=started&order=desc&datecut=9999&prefix=0",
]

num_pages = 1  # Adjust this to the desired number of pages

def decode_unicode(text):
    """Decodes any Unicode escape sequences in the text."""
    if text:
        try:
            return text.encode().decode('unicode_escape').strip()
        except Exception:
            return text.strip()
    return text

def format_date(raw_date):
    """
    Format a raw date string into ISO 8601 format.
    Handles relative dates like "yesterday" and "minutes ago".
    """
    input_format = "%d-%m-%y, %I:%M %p"
    output_format = "%Y-%m-%dT%H:%M:%S"
    now = datetime.now()

    try:
        raw_date = decode_unicode(raw_date)

        # Handle relative formats like "Today, HH:MM AM/PM"
        today_match = re.match(r"Today,\s+(\d{1,2}:\d{2}\s[APM]{2})", raw_date, re.IGNORECASE)
        if today_match:
            time_str = today_match.group(1)
            parsed_time = datetime.strptime(time_str, "%I:%M %p")
            combined_datetime = datetime.combine(now.date(), parsed_time.time())
            return combined_datetime.strftime(output_format)

        # Handle "X minutes ago" or "X hours ago"
        minutes_ago_match = re.match(r"(\d+)\s+minutes ago", raw_date, re.IGNORECASE)
        if minutes_ago_match:
            minutes_ago = int(minutes_ago_match.group(1))
            parsed_date = now - timedelta(minutes=minutes_ago)
            return parsed_date.strftime(output_format)

        hours_ago_match = re.match(r"(\d+)\s+hour(?:s)? ago", raw_date, re.IGNORECASE)
        if hours_ago_match:
            hours_ago = int(hours_ago_match.group(1))
            parsed_date = now - timedelta(hours=hours_ago)
            return parsed_date.strftime(output_format)

        # Handle "yesterday HH:MM AM/PM"
        yesterday_match = re.match(r"yesterday,\s+(\d{1,2}:\d{2}\s[APM]{2})", raw_date, re.IGNORECASE)
        if yesterday_match:
            time_str = yesterday_match.group(1)
            yesterday = now - timedelta(days=1)
            parsed_time = datetime.strptime(time_str, "%I:%M %p")
            combined_datetime = datetime.combine(yesterday.date(), parsed_time.time())
            return combined_datetime.strftime(output_format)

        # Handle absolute dates like "06-12-24, 12:12 PM"
        absolute_date_match = re.search(r"\d{2}-\d{2}-\d{2}, \d{2}:\d{2} [APM]{2}", raw_date)
        if absolute_date_match:
            absolute_date_str = absolute_date_match.group(0)
            parsed_date = datetime.strptime(absolute_date_str, input_format)
            return parsed_date.strftime(output_format)
        
        # If no known pattern matches, return None
        raise ValueError("No recognizable date format found.")
    except Exception as e:
        logging.error(f"Error formatting date: {e}")
        return raw_date

def extract_data(driver):
    """Extracts and formats data from the Selenium WebDriver."""
    try:
        title = decode_unicode(driver.find_element(By.CLASS_NAME, 'thead52323').text.strip())
    except NoSuchElementException:
        title = "No Title"

    try:
        user_element = driver.find_element(By.CLASS_NAME, 'owner')
        user = decode_unicode(user_element.text.strip())
    except NoSuchElementException:
        user = "No User"

    try:
        body = decode_unicode(driver.find_element(By.CLASS_NAME, 'post_body scaleimages').text.strip())
    except NoSuchElementException:
        body = "No Body"

    try:
        raw_date = decode_unicode(driver.find_element(By.CLASS_NAME, 'post_date').text.strip())
        formatted_date = format_date(raw_date)
    except NoSuchElementException:
        raw_date = "No Date"
        formatted_date = raw_date

    return {
        "title": title,
        "author": user,
        "content": body,
        "timestamp": formatted_date
    }

def main():
    logging.info("Starting the scraper...")

    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

    try:
        logging.info("Logging in...")
        driver.get(login_url)
        
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(login_username)
        driver.find_element(By.NAME, "password").send_keys(login_password)
        driver.find_element(By.NAME, "submit").click()

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Logout")))
        logging.info("Login successful!")

        all_data = []

        for forum_url_pattern in forum_urls:
            for page in range(1, num_pages + 1):
                forum_url = forum_url_pattern.format(page)
                logging.info(f"Fetching page: {forum_url}")
                driver.get(forum_url)
                
                time.sleep(random.uniform(3, 6))  # Simulate human interaction
                links = [a.get_attribute('href') for a in driver.find_elements(By.TAG_NAME, 'a') if 'subject_new' in a.get_attribute('href')]

                for link in links:
                    driver.get(link)
                    time.sleep(random.uniform(2, 5))
                    data = extract_data(driver)
                    data["link"] = link
                    all_data.append(data)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H")
        file_name = f"darkforums_{timestamp}.json"
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=4)
        logging.info(f"Data saved to {file_name}")

    except Exception as e:
        logging.exception("An error occurred during scraping.")
    finally:
        driver.quit()
        logging.info("Scraper finished.")

if __name__ == "__main__":
    main()
