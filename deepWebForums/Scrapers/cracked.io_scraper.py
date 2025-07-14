import requests
from bs4 import BeautifulSoup

# Start a session
session = requests.Session()

login_url = "https://cracked.io/member.php?action=login"
login_data = {
    'username': 'harry_has',  # Replace with actual username
    'password': 'NN5sk*tJ%VCTAu_',  # Replace with actual password
}

# Post login data
login_response = session.post(login_url, data=login_data)

# Verify if login was successful
if login_response.status_code == 200:
    print("Login successful!")
else:
    print("Login failed:", login_response.status_code)
    exit()  # Exit if login failed

# Base URL pattern for forum pagination
forum_url_pattern = "https://cracked.io/Forum-Other-Leaks"

# Number of pages to scrape
num_pages = 1  # Adjust this to the desired number of pages

# Loop through multiple pages
for page in range(1, num_pages + 1):
    # Format the forum URL with the current page number
    forum_url = forum_url_pattern.format(page)

    # Send a GET request to the forum page
    response = session.get(forum_url)

    # Check if the request was successful
    if response.status_code == 200:
        print(f"Scraping page {page}...")

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all spans with class "subject_new"
        all_span = soup.find_all('span', class_=' subject_new')

        # Loop through each span
        for span in all_span:
            # Find the <a> tag inside the span
            a_tag = span.find('a')

            # If an <a> tag is found, extract the href attribute
            if a_tag and 'href' in a_tag.attrs:
                href = a_tag['href']

                # Construct the full link, avoiding double slashes
                if not href.startswith('http'):
                    link = 'https://cracked.io/' + href
                else:
                    link = href

                print(link)

    else:
        print(f"Failed to scrape page {page}, status code: {response.status_code}")