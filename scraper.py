# test python
import requests

# Directus API URL for your collection (replace "your_collection" with your actual collection name)
url = "http://localhost:8055/items/webscraper_items"

try:
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad status codes (4xx, 5xx)
    
    # Print the response as JSON
    data = response.json()
    print("Items retrieved:", data)

except requests.exceptions.RequestException as e:
    print("Error during GET request:", e)


# Directus API URL for your collection (replace "your_collection" with your actual collection name)
url = "http://localhost:8055/items/webscraper_websites"

try:
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad status codes (4xx, 5xx)

    # Print the response as JSON
    data = response.json()
    print("Websites retrieved:", data)

except requests.exceptions.RequestException as e:
    print("Error during GET request:", e)
