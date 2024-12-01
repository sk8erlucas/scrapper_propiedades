import json
from datetime import datetime
import time
import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

scraper_api_key = '74576979ee1749293c025c8aeac5d0ff'

idealista_query = "https://www.idealista.com/en/venta-viviendas/barcelona-barcelona/"
scraper_api_url = f'http://api.scraperapi.com/?api_key={scraper_api_key}&url={idealista_query}'

def extract_number(text):
    return ''.join(filter(str.isdigit, text))

def get_text_or_na(element):
    return element.text.strip() if element else "N/A"

def get_phone_number(driver, listing_url):
    driver.get(listing_url)
    try:
        # Wait for the "View phone" button to be clickable
        view_phone_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.see-phones-btn"))
        )
        view_phone_button.click()
        
        # Wait for the phone number to appear
        phone_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "p.txt-big.txt-bold"))
        )
        return phone_element.text
    except TimeoutException:
        return "N/A"

# Set up Selenium WebDriver (you need to have chromedriver installed and in your PATH)
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Run in headless mode
driver = webdriver.Chrome(options=options)

response = requests.get(scraper_api_url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    house_listings = soup.find_all('article', class_='item')
    extracted_data = []

    for index, listing in enumerate(house_listings):
        listing_url = "https://www.idealista.com" + listing.find('a', class_='item-link').get('href')
        
        # Fetch detailed property page
        property_response = requests.get(f'http://api.scraperapi.com/?api_key={scraper_api_key}&url={listing_url}')
        if property_response.status_code == 200:
            property_soup = BeautifulSoup(property_response.text, 'html.parser')
            
            # Extract data from the detailed property page
            title = get_text_or_na(property_soup.find('span', class_='main-info__title-main'))
            price = get_text_or_na(property_soup.find('span', class_='info-data-price'))
            ref_portal = property_soup.find('div', class_='ide-box-detail')['id'].split('-')[-1] if property_soup.find('div', class_='ide-box-detail') else "N/A"
            advertiser_name = get_text_or_na(property_soup.find('span', class_='about-advertiser-name'))
            phone = get_phone_number(driver, listing_url)
            advertiser_type = get_text_or_na(property_soup.find('div', class_='professional-name'))
            property_type = get_text_or_na(property_soup.find('span', class_='main-info__title-minor'))
            operation = "Venta"  # Assuming it's always for sale based on the URL
            
            details = property_soup.find_all('div', class_='details-property_features')
            details_text = ' '.join([d.text for d in details])
            
            constructed_area = re.search(r'(\d+)\s*m²\s*built', details_text)
            constructed_area = constructed_area.group(1) if constructed_area else "N/A"
            
            bedrooms = re.search(r'(\d+)\s*bedrooms?', details_text)
            bedrooms = bedrooms.group(1) if bedrooms else "N/A"
            
            bathrooms = re.search(r'(\d+)\s*bathrooms?', details_text)
            bathrooms = bathrooms.group(1) if bathrooms else "N/A"
            
            floor = re.search(r'(\d+)[a-z]{2}\s*floor', details_text)
            floor = floor.group(1) if floor else "N/A"
            
            energy_rating = get_text_or_na(property_soup.find('span', class_='energy-certificate-energy-detail'))
            
            location_info = property_soup.find('div', id='headerMap')
            location_items = location_info.find_all('li') if location_info else []
            
            street = get_text_or_na(location_items[0] if len(location_items) > 0 else None)
            neighborhood = get_text_or_na(location_items[1] if len(location_items) > 1 else None)
            district = get_text_or_na(location_items[2] if len(location_items) > 2 else None)
            city = get_text_or_na(location_items[3] if len(location_items) > 3 else None)
            province = get_text_or_na(location_items[4] if len(location_items) > 4 else None)
            
            description = get_text_or_na(property_soup.find('div', class_='comment'))
            
            characteristics = ', '.join([li.text.strip() for li in property_soup.find_all('li', class_='feature')])
            
            publication_date = get_text_or_na(property_soup.find('p', class_='date-update-text'))
            
            # Extract image URLs
            image_elements = property_soup.find_all('img', class_='gallery-thumbs')
            image_urls = [img['data-ondemand-img'] for img in image_elements if 'data-ondemand-img' in img.attrs]
            
            # Calculate price per m2
            price_value = extract_number(price)
            constructed_area_value = extract_number(constructed_area)
            price_per_m2 = str(round(int(price_value) / int(constructed_area_value))) if price_value and constructed_area_value else "N/A"

            listing_data = {
                "REF. PORTAL": ref_portal,
                "NOMBRE": advertiser_name,
                "TELÉFONO": phone,
                "TIPO ANUNCIANTE": advertiser_type,
                "CATEGORÍA PROPIEDAD": property_type,
                "OPERACIÓN": operation,
                "PRECIO VENTA": price,
                "PRECIO ALQUILER": "N/A",  # Not applicable for sale listings
                "COMUNIDAD AUTÓNOMA": "Cataluña",
                "PROVINCIA": province,
                "POBLACIÓN": city,
                "COMARCA": "N/A",  # Not directly available
                "BARRIO": neighborhood,
                "POSTCODE": "N/A",  # Not directly available
                "DOMICILIO": street,
                "CALLE": street,
                "PLANTA": floor,
                "AÑO CONSTRUCCIÓN": "N/A",  # Not directly available
                "PRECIO POR M2": price_per_m2,
                "CALIFICACIÓN ENERGÉTICA": energy_rating,
                "SUPERFICIE CONSTRUIDA": constructed_area,
                "M2 TERRENO / PARCELA": "N/A",  # Not directly available
                "DORMITORIOS": bedrooms,
                "BAÑOS": bathrooms,
                "TERRAZA": "Sí" if "terrace" in details_text.lower() else "No",
                "GARAJE": "Sí" if "parking" in details_text.lower() else "No",
                "TRASTERO": "Sí" if "storage room" in details_text.lower() else "No",
                "ASCENSOR": "Sí" if "lift" in details_text.lower() else "No",
                "CARACTERÍSTICAS": characteristics,
                "TÍTULO ANUNCIO": title,
                "DESCRIPCIÓN": description,
                "ORIGEN": "Idealista",
                "URL PORTAL": listing_url,
                "FOTOS": image_urls,
                "LATITUD": "N/A",  # Not directly available
                "LONGITUD": "N/A",  # Not directly available
                "FECHA PUBLICACIÓN": publication_date,
                "FECHA EXTRACCIÓN": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "VIGENTE": "Sí",
                "STATUS": "Activo"
            }

            extracted_data.append(listing_data)
            print(f"Processed listing {index + 1}: {title}")

    current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
    json_filename = f"extracted_data_{current_datetime}.json"
    with open(json_filename, "w", encoding="utf-8") as json_file:
        json.dump(extracted_data, json_file, ensure_ascii=False, indent=2)

    print(f"Extracted data saved to {json_filename}")

else:
    print(f"Error: Unable to retrieve HTML content. Status code: {response.status_code}")

# Close the Selenium WebDriver
driver.quit()