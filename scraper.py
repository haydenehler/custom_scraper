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
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--disable-gpu")

# Use a persistent Chrome profile inside Docker
chrome_profile_path = "/chrome-profile"
chrome_options.add_argument(f"--user-data-dir={chrome_profile_path}")

os.system("pkill chrome || true")

# Set up ChromeDriver
service = Service("/usr/bin/chromedriver")  # Path to ChromeDriver in Docker
driver = webdriver.Chrome(service=service, options=chrome_options)

print("Now attempting to scrape item")

# API URLs
items_url = "http://localhost:8055/items/webscraper_items"
websites_url = "http://localhost:8055/items/webscraper_websites"

def update_item(item_id, payload):
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
                print(f"Error updating item {item_id}: {e}")
                print(f"Payload: {payload}")
                return None

def load_config(config_path="./config.json", key=None):
    with open(config_path, "r") as file:
        config = json.load(file)
    if key:
        return config.get(key, {})
    return config

def send_email(body, to_emails):
    """
    Sends an email with the given subject and body to the specified recipient(s).

    Parameters:
    - subject (str): Subject of the email.
    - body (str): Plain text body of the email.
    - to_emails (list or str): Recipient email address(es).
    - from_email (str): Sender email address.
    - smtp_server (str): SMTP server address (e.g., "smtp.gmail.com").
    - smtp_port (int): SMTP server port (e.g., 587 for TLS).
    - smtp_username (str): Username for SMTP authentication.
    - smtp_password (str): Password for SMTP authentication.
    """

    smtp_config = load_config(key="smtp")

    # Now you can access your credentials:
    smtp_server = smtp_config['smtp_server']
    smtp_port = smtp_config['smtp_port']
    smtp_username = smtp_config['smtp_username']
    smtp_password = smtp_config['smtp_password']
    from_email = smtp_config['from_email']

    # Ensure to_emails is a list
    if isinstance(to_emails, str):
        to_emails = [to_emails]

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = "hayden.ehler@gmail.com"
    message["To"] = ", ".join(to_emails)
    message["Subject"] = "Sale Notification"

    # Attach the plain text body to the email
    message.attach(MIMEText(body, "plain"))

    try:
        # Connect to the SMTP server and send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(smtp_username, smtp_password)
            server.sendmail(from_email, to_emails, message.as_string())
        print("Email sent successfully.")
    except Exception as e:
        print("Error sending email:", e)


# start here
body = ""

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

        full_url = f"{website['base_url']}{item.get('identifier', '').replace(' ', '+')}"  # Fix URL formatting
        #looking_for = website['html_class']
        looking_for = f"[{website['html_class']}]"
        print(f"Scraping URL: {full_url}")
        print(f"Looking for element: {looking_for}")

        try:
            driver.get(full_url)
            

            # Wait for the price element to be present in the DOM using WebDriverWait
            #price_element = WebDriverWait(driver, 10).until(
            #    EC.presence_of_element_located((By.CLASS_NAME, website['html_class']))
            #)
            price_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, looking_for))
            )
            price = price_element.text
            price_num = float(price.replace("$",""))
            print(f"The price of the item is: {price}")
            
            now = datetime.now().date()

            
            update_payload = {
                "current_price": price_num,
                "last_updated": now.isoformat()
            }
            # compare prices
            if item['low']:
                if price_num < item['low']:
                    update_payload.update({
                        "low": price_num
                    })
            else:
                update_payload.update({
                    "low": price_num
                })

            if item['high']:
                if price_num > item['high']:
                    update_payload.update({
                        "high": price_num
                    })
            else:
                update_payload.update({
                    "high": price_num
                })

            result = update_item(item['id'], update_payload)

            if result:
                print(f"Update successful, id: ", item['id'])

            if item['current_price']:
                if price_num < (item['current_price']*(1-item['percent_drop'])):
                    print("Item on sale!")
                    body += f"\n{item['item_name']} is down from ${item['current_price']} to ${price_num}."
                    
                else:
                    print("Item not on sale. :(")


        except Exception as e:
            print(f"Error locating price element for URL {full_url}: {e}")

            # If the element is not found, check if there's another way to fetch the price
            # You could also print out the page source for debugging
            page_source = driver.page_source
            if 'No results found' in page_source:
                print("No products found for this search.")
            else:
                print("Other error.")

        time.sleep(1)  # Add sleep between requests to avoid overloading the server

    print("test body")
    if body:
        to_emails = ["hayden.ehler@gmail.com"]
        send_email(body, to_emails)
        print("Email sent!")
    else:
        print("No email to send.")

finally:
    driver.quit()

print("Task complete.")