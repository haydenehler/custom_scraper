# test python
import requests
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")  # Required for Docker
chrome_options.add_argument("--disable-dev-shm-usage")  # Prevent crashes

# Set up ChromeDriver
service = Service("/usr/bin/chromedriver")  # Path to ChromeDriver in Docker
driver = webdriver.Chrome(service=service, options=chrome_options)

print("Now attempting to scrape item")

# API URLs
items_url = "http://localhost:8055/items/webscraper_items"
websites_url = "http://localhost:8055/items/webscraper_websites"

try:

    items_response = requests.get(items_url).json().get('data', [])
    websites_response = requests.get(websites_url).json().get('data', [])

    websites_map = {website['id']: website for website in websites_response}

    # Inside your scraping loop:
    for item in items_response:
        website = websites_map.get(item['website'])
        if not website:
            print(f"No corresponding website found for item {item['id']}")
            continue

        full_url = f"{website['base_url']}{item.get('item_name', '').replace(' ', '+')}"  # Fix URL formatting
        print(f"Scraping URL: {full_url}")

        try:
            driver.get(full_url)

            # Wait for the price element to be present in the DOM using WebDriverWait
            price_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, website['html_class']))
            )
            price = price_element.text
            print(f"The price of the item at {full_url} is: {price}")

        except Exception as e:
            print(f"Error locating price element for URL {full_url}: {e}")

            # If the element is not found, check if there's another way to fetch the price
            # You could also print out the page source for debugging
            page_source = driver.page_source
            if 'No results found' in page_source:
                print("No products found for this search.")
            else:
                print("Failed to locate element, here is the page source snippet for debugging:")
                print(page_source[:10000])  # print the first 500 chars of the page source for debugging

        # Optional: Print out the URL for clarity
            print(f"URL: {full_url}")

        time.sleep(2)  # Add sleep between requests to avoid overloading the server

finally:
    driver.quit()

def update_item(collection, item_id, payload, api_url="http://localhost:8055"):
        """
        Update an item in a Directus collection.

        :param collection: The name of the collection (e.g., "webscraper_items")
        :param item_id: The ID of the item to update
        :param payload: A dictionary containing the fields to update
        :param api_url: The base URL of the Directus API (default: "http://localhost:8055")
        :param token: Directus API access token for authentication (default: None)
        :return: The JSON response from the API
        """
        url = f"http://localhost:8055/items/webscraper_items/{item_id}"

        headers = {
                "Content-Type": "application/json"
        }

        try:
                response = requests.patch(url, data=json.dumps(payload), headers=headers)
                response.raise_for_status()  # Raise an error for bad status codes (4xx and 5xx)
                return response.json()  # Return the response as JSON
        except requests.exceptions.RequestException as e:
                print(f"Error updating item {item_id} in collection '{collection}':", e)
                return None


print("Now attempting to update item.")


# Example Usage:
collection_name = "webscraper_items"
item_id = 1
update_payload = {
	"current_price": "100"
}

result = update_item(collection_name, item_id, update_payload)
if result:
	print("Update successful:", result)

