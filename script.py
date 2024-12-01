import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup


scraper_api_key = '74576979ee1749293c025c8aeac5d0ff'


idealista_query = "https://www.idealista.com/en/venta-viviendas/barcelona-barcelona/"
scraper_api_url = f'http://api.scraperapi.com/?api_key={
    scraper_api_key}&url={idealista_query}'


response = requests.get(scraper_api_url)


# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract each house listing post
    house_listings = soup.find_all('article', class_='item')

    # Create a list to store extracted information
    extracted_data = []

    # Loop through each house listing and extract information
    for index, listing in enumerate(house_listings):
        # Extracting relevant information
        title = listing.find('a', class_='item-link').get('title')
        price = listing.find('span', class_='item-price').text.strip()

        # Find all div elements with class 'item-detail'
        item_details = listing.find_all('span', class_='item-detail')

        # Extracting bedrooms and area from the item_details
        bedrooms = item_details[0].text.strip(
        ) if item_details and item_details[0] else "N/A"
        area = item_details[1].text.strip() if len(
            item_details) > 1 and item_details[1] else "N/A"

        description = listing.find('div', class_='item-description').text.strip(
        ) if listing.find('div', class_='item-description') else "N/A"
        tags = listing.find('span', class_='listing-tags').text.strip(
        ) if listing.find('span', class_='listing-tags') else "N/A"

        # URL of the listing
        listing_url = "https://www.idealista.com" + listing.find('a', class_='item-link').get('href')

        # Extracting images
        image_elements = listing.find_all('img')
        print(image_elements)
        image_tags = [img.prettify()
                      for img in image_elements] if image_elements else []
        print(image_tags)

        # Store extracted information in a dictionary
        listing_data = {
            "Title": title,
            "Price": price,
            "Bedrooms": bedrooms,
            "Area": area,
            "Description": description,
            "Tags": tags,
            "URL": listing_url,
            "Image Tags": image_tags
        }

        # Append the dictionary to the list
        extracted_data.append(listing_data)

        # Print or save the extracted information (you can modify this part as needed)
        print(f"Listing {index + 1}:")
        print(f"Title: {title}")
        print(f"Price: {price}")
        print(f"Bedrooms: {bedrooms}")
        print(f"Area: {area}")
        print(f"Description: {description}")
        print(f"Tags: {tags}")
        print(f"Image Tags: {', '.join(image_tags)}")
        print("=" * 50)

    # Save the extracted data to a JSON file
    current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
    json_filename = f"extracted_data_{current_datetime}.json"
    with open(json_filename, "w", encoding="utf-8") as json_file:
        json.dump(extracted_data, json_file, ensure_ascii=False, indent=2)

    print(f"Extracted data saved to {json_filename}")


else:
    print(f"Error: Unable to retrieve HTML content. Status code: {
          response.status_code}")
