import requests
import pandas as pd
from bs4 import BeautifulSoup


l = list()
o = {}

target_url = "https://www.idealista.com/venta-viviendas/torrelavega/inmobiliaria-barreda/"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36", "Accept-Language": "en-US,en;q=0.9",
           "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", "Accept-Encoding": "gzip, deflate, br", "upgrade-insecure-requests": "1"}

resp = requests.get(
    "https://api.scrapingdog.com/scrape?api_key=674bc2de76025bde66024c0d&url={}&dynamic=false".format(target_url))

print(resp.status_code)
soup = BeautifulSoup(resp.text, 'html.parser')

allProperties = soup.find_all("div", {"class": "item-info-container"})

for i in range(0, len(allProperties)):
    o["title"] = allProperties[i].find(
        "a", {"class": "item-link"}).text.strip("\n")
    o["price"] = allProperties[i].find(
        "span", {"class": "item-price"}).text.strip("\n")
    o["area-size"] = allProperties[i].find("div",
                                           {"class": "item-detail-char"}).text.strip("\n")
    o["description"] = allProperties[i].find(
        "div", {"class": "item-description"}).text.strip("\n")
    o["property-link"] = "https://www.idealista.com" + \
        allProperties[i].find("a", {"class": "item-link"}).get('href')
    l.append(o)
    o = {}


print(l)

# Guardar la lista 'l' en un archivo Excel
df = pd.DataFrame(l)
df.to_excel("propiedades_idealista.xlsx", index=False)
print("Los datos se han guardado en 'propiedades_idealista.xlsx'")
