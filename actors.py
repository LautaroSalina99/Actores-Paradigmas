from bs4 import BeautifulSoup
import requests
from thespian.actors import Actor
from urllib.parse import urlparse
from scrapers import scrape_mercadolibre, scrape_tiendamia, scrape_fullh4rd

class ScraperActor(Actor):
    def receiveMessage(self, message, sender):
        url = message
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        domain = urlparse(url).netloc

        if 'mercadolibre.com' in domain:
            price, availability, promotion, description = scrape_mercadolibre(soup)
        elif 'tiendamia.com' in domain:
            price, availability, promotion = scrape_tiendamia(soup)
            description = 'N/A'
        elif 'fullh4rd.com' in domain:
            price, availability, promotion, description = scrape_fullh4rd(soup)
        else:
            price, availability, promotion, description = 'Dominio no soportado', 'N/A', 'N/A', 'N/A'

        self.send(sender, (url, price, availability, promotion, description))

class CompareActor(Actor):
    def receiveMessage(self, message, sender):
        prices = message
        valid_prices = [(source, price, avail, promo, desc) for source, price, avail, promo, desc in prices if price != 'No encontrado' and price != 'Dominio no soportado']
        
        if valid_prices:
            best_price = min(valid_prices, key=lambda x: float(x[1].replace(',', '').replace('.', '')))
            result = (
                f"Mejor precio: {best_price[1]} en {best_price[0]}\n"
                f"Disponibilidad: {best_price[2]}\n"
                f"Promoción: {best_price[3]}\n"
                f"Descripción: {best_price[4][:2000]}..."
            )
        else:
            result = "No se encontraron precios válidos."

        self.send(sender, result)
