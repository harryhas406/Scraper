import requests
from bs4 import BeautifulSoup
import tempfile
import time
import random
import json
import os
from datetime import datetime, timedelta
import re

# Define a list of User-Agents to rotate between
user_agents = [
    # 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
    # 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
    # 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/92.0 Safari/537.36',
    # 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15',
    # 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
]

# Start a session
session = requests.Session()

login_url = "https://darkforums.st/member.php?action=login"
login_data = {
    'username': 'harry_has',  # Replace with actual username
    'password': 'ZXCvbnm0',  # Replace with actual password
}

# Post login data
login_response = session.post(
    login_url,
    data=login_data,
    allow_redirects=True
)
# Capture session cookies after login
session_cookies = login_response.cookies  # Extract cookies

# Verify if login was successful
if login_response.status_code == 200:
    print("Login successful!")
else:
    print("Login failed:", login_response.status_code)
    exit()  # Exit if login failed

# Base URL pattern for forum pagination
forum_urls = [
    "https://darkforums.st/Forum-Databases?page={}&sortby=started&order=desc&datecut=9999&prefix=0",
    "https://darkforums.st/Forum-Other-Leaks?page={}&sortby=started&order=desc&datecut=9999&prefix=0",
    "https://darkforums.st/Forum-Stealer-Logs?page={}&sortby=started&order=desc&datecut=9999&prefix=0",
    "https://darkforums.st/Forum-Cracked-Accounts?page={}&sortby=started&order=desc&datecut=9999&prefix=0",
    "https://darkforums.st/Forum-Combolists?page={}&sortby=started&order=desc&datecut=9999&prefix=0"
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
    Handles absolute dates (e.g., "06-12-24, 12:12 PM") and relative dates 
    (e.g., "33 minutes ago", "yesterday 12:12pm").
    """
    input_format = "%d-%m-%y, %I:%M %p"
    output_format = "%Y-%m-%dT%H:%M:%S"
    now = datetime.now()
    
    try:
        # Decode Unicode in the raw date first
        raw_date = decode_unicode(raw_date)

        # Handle "Today, HH:MM AM/PM"
        today_match = re.match(r"Today,\s+(\d{1,2}:\d{2}\s[APM]{2})", raw_date, re.IGNORECASE)
        if today_match:
            time_str = today_match.group(1)
            parsed_time = datetime.strptime(time_str, "%I:%M %p")
            combined_datetime = datetime.combine(now.date(), parsed_time.time())
            return combined_datetime.strftime(output_format)
        
        # Handle "X minutes ago"
        minutes_ago_match = re.match(r"(\d+)\s+minutes ago", raw_date, re.IGNORECASE)
        if minutes_ago_match:
            minutes_ago = int(minutes_ago_match.group(1))
            parsed_date = now - timedelta(minutes=minutes_ago)
            return parsed_date.strftime(output_format)
        
        # Handle "X hours ago"
        hours_ago_match = re.match(r"(\d+)\s+hour(?:s)? ago", raw_date, re.IGNORECASE)
        if hours_ago_match:
            hours_ago = int(hours_ago_match.group(1))
            parsed_date = now - timedelta(hours=hours_ago)
            return parsed_date.strftime(output_format)

        # Handle "yesterday HH:MMam/pm"
        yesterday_match = re.match(r"yesterday,\s+(\d{1,2}:\d{2}\s[APM]{2})", raw_date, re.IGNORECASE)
        if yesterday_match:
            time_str = yesterday_match.group(1)
            yesterday = now - timedelta(days=1)
            parsed_time = datetime.strptime(time_str, "%I:%M %p")
            combined_datetime = datetime.combine(yesterday.date(), parsed_time.time())
            return combined_datetime.strftime(output_format)

        # Handle absolute date format
        primary_date_match = re.search(r"\d{2}-\d{2}-\d{2}, \d{2}:\d{2} [APM]{2}", raw_date)
        if primary_date_match:
            primary_date_str = primary_date_match.group(0)
            parsed_date = datetime.strptime(primary_date_str, input_format)
            return parsed_date.strftime(output_format)

        # If no known pattern matches, return None
        raise ValueError("No recognizable date format found.")
    except Exception as e:
        print(f"Error formatting date: {e}")
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

# Create a temporary file for storing links
with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt') as temp_file:
    temp_file_path = temp_file.name
    print(f"Temporary file created: {temp_file_path}")

    # Loop through each forum URL
    for forum_url_pattern in forum_urls:
        print(f"Scraping forum: {forum_url_pattern}")

        # Loop through the pages of each forum
        for page in range(1, num_pages + 1):
            headers = {"User-Agent": random.choice(user_agents)}
            forum_url = forum_url_pattern.format(page)

            # Add a random delay before each request
            time.sleep(random.uniform(3, 8))

            # Fetch the forum page
            response = session.get(forum_url, headers=headers, cookies=session_cookies)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                all_spans = soup.find_all('span', class_='subject_new')

                # Extract links from the page
                for span in all_spans:
                    a_tag = span.find('a')
                    if a_tag and 'href' in a_tag.attrs:
                        href = a_tag['href']
                        link = 'https://darkforums.st/' + href if not href.startswith('http') else href
                        print(link)
                        temp_file.write(link + '\n')

    temp_file.flush()

all_data = []

# Read links from the temp file and process each
with open(temp_file_path, 'r') as file:
    for link in file:
        link = link.strip()
        response = session.get(link)
        if response.status_code == 200:
            print(f"Scraping details from {link}...")
            soup = BeautifulSoup(response.content, 'html.parser')
            data = extract_data(soup)
            data["link"] = link  # Associate the link with its data
            all_data.append(data)
        else:
            print(f"Failed to retrieve: {link}")
        time.sleep(random.uniform(2, 5))  # Add delay between requests

# Save all data to a JSON file with timestamp and forum name
forum_name = forum_urls[0].split('/')[2]  # Extract forum name from the first URL
timestamp = datetime.now().strftime("%Y-%m-%d_%H")  # Current date and time
file_name = f"{forum_name}_{timestamp}.json"  # Construct file name

with open(file_name, mode="w", encoding="utf-8") as file:
    json.dump(all_data, file, indent=4)
print(f"Data saved to {file_name}")
