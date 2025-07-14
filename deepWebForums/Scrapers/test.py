import requests
from bs4 import BeautifulSoup
import tempfile
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

# Define a list of User-Agents to rotate between
user_agents = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
]

# Login URL and credentials
login_url = "https://darkforums.st/member.php?action=login"
login_data = {
    'username': 'harry_has',  # Replace with actual username
    'password': 'ZXCvbnm0',  # Replace with actual password
}

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


def extract_data(soup):
    """Extracts and formats data from a BeautifulSoup object."""
    title = decode_unicode(soup.find('div', class_='thead52323').text.strip()) if soup.find('div', class_='thead52323') else "No Title"
    user_element = (soup.find('span', class_='owner') or
                    soup.find('span', class_='df_i df_god') or
                    soup.find('span', class_='admin') or
                    soup.find('span', class_='memrpc') or
                    soup.find('span', class_='largetext') or
                    soup.find('span', class_='adminrpc'))
    user = decode_unicode(user_element.text.strip()) if user_element else "No User"
    body = decode_unicode(soup.find('div', class_='post_body scaleimages').text.strip()) if soup.find('div', class_='post_body scaleimages') else "No Body"
    raw_date = decode_unicode(soup.find('span', class_='post_date').text.strip()) if soup.find('span', class_='post_date') else "No Date"

    # Format the date to ISO 8601 for Elasticsearch
    formatted_date = format_date(raw_date) if raw_date != "No Date" else raw_date

    # Optionally extract and format "last modified" date
    modified_date_match = re.search(r"last modified: (.+)", raw_date, re.IGNORECASE)
    last_modified_date = format_date(modified_date_match.group(1)) if modified_date_match else None

    return {
        "title": title,
        "author": user,
        "content": body,
        "timestamp": formatted_date,
        "last_modified": last_modified_date
    }


# Start the scraping process
logging.info("Starting the scraper...")
session = requests.Session()

try:
    headers = {"User-Agent": random.choice(user_agents)}
    logging.info("Logging in...")
    login_response = session.post(login_url, data=login_data, headers=headers)
    if login_response.status_code == 200 and "Logout" in login_response.text:
        print(login_response.text)
        logging.info("Login successful!")
    else:
        print(login_response.text)
        print("Request Headers:", login_response.request.headers)
        print("Response Headers:", login_response.headers)
        logging.error("Login failed. Status code: %s", login_response.status_code)
        raise ValueError("Login failed. Check credentials or website changes.")

    temp_file_path = tempfile.NamedTemporaryFile(delete=False).name
    logging.info(f"Temporary file created: {temp_file_path}")

    all_data = []

    for forum_url_pattern in forum_urls:
        for page in range(1, num_pages + 1):
            forum_url = forum_url_pattern.format(page)
            logging.info(f"Fetching page: {forum_url}")
            time.sleep(random.uniform(3, 8))
            response = session.get(forum_url, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                links = [a['href'] for a in soup.find_all('a', href=True) if 'subject_new' in str(a)]
                with open(temp_file_path, 'a') as temp_file:
                    for link in links:
                        temp_file.write(link + '\n')

    with open(temp_file_path, 'r') as file:
        for link in file:
            link = link.strip()
            response = session.get(link, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                data = extract_data(soup)
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
    os.remove(temp_file_path)
    logging.info("Temporary file deleted.")
