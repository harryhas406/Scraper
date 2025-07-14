import requests
from bs4 import BeautifulSoup
import tempfile
import time
import random
import json
import os
from datetime import datetime

# Define a list of User-Agents to rotate between
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/92.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15',
]

# Start a session 
session = requests.Session()

login_url = "https://darkforums.st/member.php?action=login"
login_data = {
    'username': 'harry_has',  # Replace with actual username
    'password': 'ZXCvbnm0',  # Replace with actual password
}

# Post login data
# Login attempt with rotating User-Agent and Proxy
login_response = session.post(
    login_url,
    data=login_data,
)
# Verify if login was successful
if login_response.status_code == 200:
    print("Login successful!")
else: 
    print("Login failed:", login_response.status_code)
    exit()  # Exit if login failed

# Base URL pattern for forum pagination
# List of forum URL patterns (each with its unique pagination structure)
forum_urls = [
    "https://darkforums.st/Forum-Databases?page={}&sortby=started&order=desc&datecut=9999&prefix=0",
    "https://darkforums.st/Forum-Other-Leaks?page={}&sortby=started&order=desc&datecut=9999&prefix=0",
    "https://darkforums.st/Forum-Stealer-Logs?page={}&sortby=started&order=desc&datecut=9999&prefix=0",
    "https://darkforums.st/Forum-Cracked-Accounts?page={}&sortby=started&order=desc&datecut=9999&prefix=0",
    "https://darkforums.st/Forum-Combolists?page={}&sortby=started&order=desc&datecut=9999&prefix=0"
]
# Number of pages to scrape
num_pages = 1  # Adjust this to the desired number of pages


def extract_data(soup):
    # Extracting the title, user, body, and date fields
    title = soup.find('div', class_='thead52323').text.strip() if soup.find('div', class_='thead52323') else "No Title"
    user_element = (soup.find('span', class_='owner') or
                    soup.find('span', class_='df_i df_god') or
                    soup.find('span', class_='admin') or
                    soup.find('span', class_='memrpc') or
                    soup.find('span', class_='largetext') or
                    soup.find('span', class_='adminrpc'))
    user = user_element.text.strip() if user_element else "No User"
    body = soup.find('div', class_='post_body scaleimages').text.strip() if soup.find('div', class_='post_body scaleimages') else "No Body"
    raw_date = soup.find('span', class_='post_date').text.strip() if soup.find('span', class_='post_date') else "No Date"
    
    # Format the date to ISO 8601 for Elasticsearch
    formatted_date = None
    if raw_date and raw_date != "No Date":
        try:
            # Define the input format of the date
            input_format = "%d-%m-%y, %I:%M %p"  # Match the raw date format
            # Parse and format the date
            parsed_date = datetime.strptime(raw_date, input_format)
            formatted_date = parsed_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            formatted_date = raw_date

    # Return extracted data as a dictionary
    return {
        "title": title,
        "user": user,
        "body": body,
        "date": formatted_date if formatted_date else raw_date,  # Use formatted_date if valid
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
            response = session.get(forum_url)
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
forum_name = forum_url_pattern.split('/')[2].split('/')[0]  # Extract forum name from URL
timestamp = datetime.now().strftime("%Y-%m-%d_%H")  # Current date and time
file_name = f"{forum_name}_{timestamp}.json"  # Construct file name

with open(file_name, mode="w", encoding="utf-8") as file:
    json.dump(all_data, file, indent=4)
print(f"Data saved to {file_name}")

# # Save all data to a JSON file
# with open("extracted_data.json", mode="w", encoding="utf-8") as file:
#     json.dump(all_data, file, indent=4)

# print("Data saved to extracted_data.json")



# import requests
# from bs4 import BeautifulSoup

# # Start a session
# session = requests.Session()

# login_url = "https://darkforums.st/member.php?action=login"
# login_data = {
#     'username': 'harry_has',  # Replace with actual username
#     'password': 'ZXCvbnm0',  # Replace with actual password
# }

# # Post login data
# login_response = session.post(login_url, data=login_data)

# # Verify if login was successful
# if login_response.status_code == 200:
#     print("Login successful!")
# else:
#     print("Login failed:", login_response.status_code)
#     exit()  # Exit if login failed

# # Base URL pattern for forum pagination
# forum_url_pattern = "https://darkforums.st/Forum-Other-Leaks?page={}"

# # Number of pages to scrape
# num_pages = 3  # Adjust this to the desired number of pages

# # Loop through multiple pages
# for page in range(1, num_pages + 1):
#     # Format the forum URL with the current page number
#     forum_url = forum_url_pattern.format(page)

#     # Send a GET request to the forum page
#     response = session.get(forum_url)

#     # Check if the request was successful
#     if response.status_code == 200:
#         print(f"Scraping page {page}...")

#         # Parse the HTML content with BeautifulSoup
#         soup = BeautifulSoup(response.content, 'html.parser')

#         # Find all spans with class "subject_new"
#         all_spans = soup.find_all('span', class_='subject_new')

#         # Loop through each span
#         for span in all_spans:
#             # Find the <a> tag inside the span
#             a_tag = span.find('a')

#             # If an <a> tag is found, extract the href attribute
#             if a_tag and 'href' in a_tag.attrs:
#                 href = a_tag['href']

#                 # Construct the full link, avoiding double slashes
#                 if not href.startswith('http'):
#                     link = 'https://darkforums.st/' + href
#                 else:
#                     link = href

#                 print(link)

#     else:
#         print(f"Failed to scrape page {page}, status code: {response.status_code}")