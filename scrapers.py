import requests
from bs4 import BeautifulSoup
import re

def scrape_mercadolibre(soup):
    price_tag = soup.find('meta', {'itemprop': 'price'})
    price = price_tag['content'] if price_tag else 'No encontrado'
    
    available_tag = soup.find('span', {'class': 'ui-pdp-buybox__quantity__available'})
    availability = available_tag.text.strip() if available_tag else 'Disponibilidad desconocida'
    
    promotion_tag = soup.find('span', {'class': 'ui-pdp-price__second-line__sale-price'})
    promotion = 'En promoción' if promotion_tag else 'Sin promoción'

    description = ''
    description_div = soup.find('div', {'class': 'ui-pdp-description'})
    if description_div:
        description = description_div.get_text(strip=True)

    return price, availability, promotion, description

def scrape_tiendamia(soup):
    price_tag = soup.find('span', class_='currency_price')
    price = price_tag.text.strip().replace('AR$', '').replace('.', '').replace(',', '.') if price_tag else 'No encontrado'

    available_tag = soup.find('div', {'class': 'product-information'})
    availability = available_tag.text.strip() if available_tag else 'Disponibilidad desconocida'
    
    promotion_tag = soup.find('div', {'class': 'badge-sale'})
    promotion = 'En promoción' if promotion_tag else 'Sin promoción'

    return price, availability, promotion

def scrape_fullh4rd(soup):
    price_tag = soup.find('div', {'class': 'price-special-container'})
    price = 'No encontrado'
    if price_tag:
        price_text = price_tag.text.strip()
        price_match = re.search(r'\$\s*(\d+(?:\.\d+)?)', price_text)
        if price_match:
            price = price_match.group(1)

    available_tag = soup.find('span', {'class': 'availability-status'})
    availability = available_tag.text.strip() if available_tag else 'Disponibilidad desconocida'

    promotion_tag = soup.find('div', {'class': 'promotion-label'})
    promotion = 'En promoción' if promotion_tag else 'Sin promoción'

    description = ''
    info_div = soup.find('div', class_='info air')
    if info_div:
        description = ' '.join(info_div.stripped_strings)

    return price, availability, promotion, description

#BUEN CODIGO