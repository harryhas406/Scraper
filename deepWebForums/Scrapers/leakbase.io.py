# import requests
# from bs4 import BeautifulSoup
# import tempfile
# import time
# import random
# import json

# # Define a list of User-Agents to rotate between
# user_agents = [
#     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
#     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
#     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/92.0 Safari/537.36',
#     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15',
# ]

# # Start a session
# session = requests.Session()

# login_url = "https://leakbase.io/member.php?action=login"
# login_data = {
#     'username': 'has_harry',  # Replace with actual username
#     'password': 'ZXCVbnm0',  # Replace with actual password
# }

# # Post login data
# # Login attempt with rotating User-Agent and Proxy
# login_response = session.post(
#     login_url,
#     data=login_data,
#     headers={"User-Agent": random.choice(user_agents)}
# )
# # Verify if login was successful
# if login_response.status_code == 200:
#     print("Login successful!")
# else:
#     print("Login failed:", login_response.status_code)
#     exit()  # Exit if login failed

# # Base URL pattern for forum pagination
# forum_url_pattern = "https://leakbase.io/forums/big/page-{}?order=post_date&direction=desc"

# # Number of pages to scrape
# num_pages = 3  # Adjust this to the desired number of pages

# # Define the data extraction function
# def extract_data(soup):
#     # Extracting the title, user, body, and date fields
#     title = soup.find('div', class_='thead52323').text.strip() if soup.find('div', class_='thead52323') else "No Title"
#     user_element = (soup.find('span', class_='owner') or
#                     soup.find('span', class_='df_i df_god') or
#                     soup.find('span', class_='admin') or
#                     soup.find('span', class_='memrpc') or
#                     soup.find('span', class_='adminrpc'))
#     user = user_element.text.strip() if user_element else "No User"
#     body = soup.find('div', class_='post_body scaleimages').text.strip() if soup.find('div', class_='post_body scaleimages') else "No Body"
#     date = soup.find('span', class_='post_date').text.strip() if soup.find('span', class_='post_date') else "No Date"
    
#     # Return extracted data as a dictionary
#     return {

#         "title": title,
#         "user": user,
#         "body": body,
#         "date": date
# }

# # Create a temporary file for storing the links
# with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt') as temp_file:
#     temp_file_path = temp_file.name
#     print(f"Temporary file created: {temp_file_path}")

#     # Loop through multiple pages
#     for page in range(1, num_pages + 1):
#         # Rotate User-Agent and Proxy for each request
#         headers = {"User-Agent": random.choice(user_agents)}

#         # Format the forum URL with the current page number
#         forum_url = forum_url_pattern.format(page)

#         # Add a random delay before each request
#         time.sleep(random.uniform(3, 8))  # Delay between 3 to 8 seconds

#         # Send a GET request to the forum page
#         response = session.get(forum_url, headers=headers)

#         # Check if the request was successful
#         if response.status_code == 200:
#             print(f"Scraping page {page}...")

#             # Parse the HTML content with BeautifulSoup
#             soup = BeautifulSoup(response.content, 'html.parser')

#             # Find all spans with class "subject_new"
#             all_spans = soup.find_all('span', class_='subject_new')

#             # Loop through each span
#             for span in all_spans:
#                 # Find the <a> tag inside the span
#                 a_tag = span.find('a')

#                 # If an <a> tag is found, extract the href attribute
#                 if a_tag and 'href' in a_tag.attrs:
#                     href = a_tag['href']

#                     # Construct the full link, avoiding double slashes
#                     if not href.startswith('http'):
#                         link = 'https://darkforums.st/' + href
#                     else:
#                         link = href

#                     # Print and write the link to the temp file
#                     print(link)
#                     temp_file.write(link + '\n')  # Write each link on a new line

#     # After the loop, flush the written data to the disk
#     temp_file.flush()

# all_data = []
# # Read from the temp file and scrape each link for required fields
# # Inside the link scraping loop, modify to include links with data
# with open(temp_file_path, 'r') as file:
#     for link in file:
#         link = link.strip()  # Remove any leading/trailing whitespace

#         try:
#             # Send a GET request to each individual link
#             response = session.get(link, timeout=10)  # Set a timeout

#             if response.status_code == 200:
#                 print(f"Scraping details from {link}...")

#                 # Parse the HTML content
#                 soup = BeautifulSoup(response.content, 'html.parser')

#                 data = extract_data(soup)
#                 # Include link in the extracted data
#                 all_data.append({"link": link, **data})  # Add link to data

#             else:
#                 print(f"Failed to retrieve the page: {link} (Status Code: {response.status_code})")
        
#         except requests.exceptions.RequestException as e:
#             print(f"An error occurred: {e}")

# # Save the collected data to a JSON file as an array
# with open("leakbase_data.json", mode="w", encoding="utf-8") as file:
#     json.dump(all_data, file, indent=4)

# print("Data saved to leakbase_data.json")

# ------------------------------------------------------------------------------------------------------------------------------------------------------------#

# import requests
# import time
# import random
# from bs4 import BeautifulSoup

# # Start a session
# session = requests.Session()

# # Common headers list to mimic real browser requests
# headers_list = [
#     {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
#         'Accept-Language': 'en-US,en;q=0.9',
#     },
#     {
#         'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:85.0) Gecko/20100101 Firefox/85.0',
#         'Accept-Language': 'en-US,en;q=0.9',
#     },
#     {
#         'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36',
#         'Accept-Language': 'en-US,en;q=0.9',
#     },
# ] 

# # List of base URLs to scrape (without the page number)
# base_urls = [
#     "https://leakbase.io/forums/big/page-{}?order=post_date&direction=desc",
#     "https://leakbase.io/forums/apbchucky/page-{}",
#     "https://leakbase.io/forums/cloud/page-{}?order=post_date&direction=desc",
#     "https://leakbase.io/forums/country/page-{}?order=post_date&direction=desc",
#     "https://leakbase.io/forums/dehashed/page-{}?order=post_date&direction=desc",
# ]

# # Number of pages to scrape
# num_pages = 3  # Adjust this to the desired number of pages

# # Open a file to save the scraped links
# with open("leakbase.io_links.txt", "a") as file:
#     for base_url in base_urls:
#         # Loop through multiple pages
#         for page in range(1, num_pages + 1):
#             # Format the forum URL with the current page number
#             forum_url = base_url.format(page)

#             # Choose a random user-agent for each request
#             headers = random.choice(headers_list)

#             # Send a GET request to the URL with headers
#             response = session.get(forum_url, headers=headers)

#             # Check if the request was successful
#             if response.status_code == 200:
#                 print(f"Scraping page {page} of {forum_url}...")

#                 # Parse the HTML content with BeautifulSoup
#                 soup = BeautifulSoup(response.content, 'html.parser')

#                 # Print the HTML content to inspect the structure
#                 print(soup.prettify())  # <-- Debug: print full page HTML for inspection

#                 # Find all divs with class "structItem-title" (adjust as necessary)
#                 all_div = soup.find_all('div', class_='structItem-title')

#                 if not all_div:
#                     print("No matching divs found. Check the class name and structure.")

#                 # Loop through each div
#                 for div in all_div:
#                     # Find the <a> tag inside the div
#                     a_tag = div.find('a')

#                     # If an <a> tag is found, extract the href attribute
#                     if a_tag and 'href' in a_tag.attrs:
#                         href = a_tag['href']

#                         # Construct the full link
#                         if not href.startswith('http'):
#                             link = 'https://leakbase.io' + href
#                         else:
#                             link = href

#                         # Print and save the link to the file
#                         print(link)
#                         file.write(link + "\n")  # Save each link on a new line
            
#                 # Add a random delay between requests to avoid rate limiting
#                 time.sleep(random.uniform(2, 5))  # Random delay between 2 to 5 seconds
#             else:
#                 print(f"Failed to scrape page {page} of {forum_url}, status code: {response.status_code}")

# ------------------------------------------------------------------------------------------------------------------------------------------------- #

# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import time
# import random

# # Set up Chrome options
# chrome_options = Options()
# chrome_options.add_argument("--headless")  # Run headlessly
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")

# # Path to your ChromeDriver
# service = Service('/home/cdot/Downloads/chromedriver-linux64 (v130)/chromedriver-linux64/chromedriver')  # Update this path

# # Start a new browser session
# driver = webdriver.Chrome(service=service, options=chrome_options)

# # List of base URLs to scrape (without the page number)
# base_urls = [
#     "https://leakbase.io/forums/big/page-{}?order=post_date&direction=desc",
#     "https://leakbase.io/forums/apbchucky/page-{}",
#     "https://leakbase.io/forums/cloud/page-{}?order=post_date&direction=desc",
#     "https://leakbase.io/forums/country/page-{}?order=post_date&direction=desc",
#     "https://leakbase.io/forums/dehashed/page-{}?order=post_date&direction=desc",
# ]

# # Number of pages to scrape
# num_pages = 3  # Adjust this as needed

# # Open a file to save the scraped links
# with open("scraped_links.txt", "a") as file:
#     for base_url in base_urls:
#         for page in range(1, num_pages + 1):
#             # Construct the full URL
#             forum_url = base_url.format(page)
#             print(f"Constructed URL: {forum_url}")  # Debug print statement

#             # Load the page
#             print(f"Scraping page {page} of {forum_url}...")
#             driver.get(forum_url)

#             # Wait for the page to load and the relevant elements to be present
#             print("Waiting for the page to load...")
#             try:
#                 WebDriverWait(driver, 10).until(
#                     EC.presence_of_all_elements_located((By.CLASS_NAME, 'structItem-title'))
#                 )
#             except Exception as e:
#                 print("Error waiting for page to load:", e)
#                 continue  # Skip to the next page if the current one fails to load


#             # Find all divs with class "structItem-title"
#             all_divs = driver.find_elements(By.CLASS_NAME, 'structItem-title')
#             print(f"Found {len(all_divs)} div(s) with class 'structItem-title' on page {page}.")  # Debug print statement

#             if not all_divs:
#                 print(f"No matching divs found on page {page} of {forum_url}")
#             else:
#                 for div in all_divs:
#                     a_tag = div.find_element(By.TAG_NAME, 'a')
#                     if a_tag and 'href' in a_tag.get_attribute('href'):
#                         link = a_tag.get_attribute('href')
#                         print("Found link:", link)
#                         file.write(link + "\n")  # Write link to file
#                     else:
#                         print("No <a> tag found in div or <a> tag does not contain 'href'.")  # Debug print statement

#             # Add a random delay between requests to avoid rate limiting
#             print("Adding a random delay before the next request...")
#             time.sleep(random.uniform(2, 5))  # 2-5 seconds delay

# # Close the browser
# print("Closing the browser...")
# driver.quit()
# print("Scraping completed. All links have been saved.")

# ---------------------------------------------------------------------------------------------------------------------------------------- #

import requests
import time
import random
from bs4 import BeautifulSoup

# Start a session
session = requests.Session()

# Set headers to mimic a real browser
headers_list = [
    {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) Gecko/20100101 Firefox/101.0"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"}
]

# Base URL pattern for forum pagination
forum_url_pattern = "https://leakbase.io/forums/big"

# Number of pages to scrape
num_pages = 3  # Adjust this to the desired number of pages

# Loop through multiple pages
for page in range(1, num_pages + 1):
    # Format the forum URL with the current page number
    forum_url = forum_url_pattern.format(page)
    
    # Choose a random user-agent for each request
    headers = random.choice(headers_list)

    # Send a GET request to the forum page with headers
    response = session.get(forum_url)

    # Check if the request was successful
    if response.status_code == 200:
        print(f"Scraping page {page}...")

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all divs with class "structItem-title"
        all_divs = soup.find_all('div', class_='structItem-title')

        # Loop through each div
        for div in all_divs:
            # Find the <a> tag inside the span
            a_tag = div.find('a')

            # If an <a> tag is found, extract the href attribute
            if a_tag and 'href' in a_tag.attrs:
                href = a_tag['href']

                # Construct the full link, avoiding double slashes
                if not href.startswith('http'):
                    link = 'https://leakbase.io' + href
                else:
                    link = href

                print(link)

        # Add a random delay between requests to avoid rate limiting
        time.sleep(random.uniform(5, 7))  # Random delay between 2 to 5 seconds
    else:
        print(f"Failed to scrape page {page}, status code: {response.status_code}")
