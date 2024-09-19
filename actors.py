from bs4 import BeautifulSoup  # Librería para analizar el HTML de las páginas web
import requests  # Para realizar solicitudes HTTP y obtener el contenido de las páginas web
from thespian.actors import Actor  # Para definir actores utilizando la librería Thespian
from urllib.parse import urlparse  # Para extraer el dominio de una URL
from scrapers import scrape_mercadolibre, scrape_tiendamia, scrape_fullh4rd  # Funciones de scraping específicas de cada sitio

# Definición de la clase ScraperActor, que hereda de Actor
class ScraperActor(Actor):
    def receiveMessage(self, message, sender):
        # La URL que se va a scrapear es recibida como un mensaje
        url = message
        
        # Realiza una solicitud GET a la URL y obtiene el contenido HTML de la página
        response = requests.get(url)
        
        # Convierte el contenido HTML en un objeto BeautifulSoup para poder analizarlo
        soup = BeautifulSoup(response.content, 'html.parser')

        # Obtiene el dominio de la URL utilizando urlparse para decidir qué scraper usar
        domain = urlparse(url).netloc

        # Verifica si la URL pertenece a MercadoLibre y usa el scraper correspondiente
        if 'mercadolibre.com' in domain:
            price, availability, promotion, description = scrape_mercadolibre(soup)
        # Verifica si la URL pertenece a TiendaMia y usa el scraper correspondiente
        elif 'tiendamia.com' in domain:
            price, availability, promotion = scrape_tiendamia(soup)
            description = 'N/A'  # Si no hay descripción en TiendaMia, se asigna 'N/A'
        # Verifica si la URL pertenece a FullH4rd y usa el scraper correspondiente
        elif 'fullh4rd.com' in domain:
            price, availability, promotion, description = scrape_fullh4rd(soup)
        # Si el dominio no es soportado, asigna valores predeterminados indicando un error
        else:
            price, availability, promotion, description = 'Dominio no soportado', 'N/A', 'N/A', 'N/A'

        # Envía los resultados de la extracción (precio, disponibilidad, promoción, descripción) al actor que envió el mensaje
        self.send(sender, (url, price, availability, promotion, description))


# Definición de la clase CompareActor, que también hereda de Actor
class CompareActor(Actor):
    def receiveMessage(self, message, sender):
        # Recibe una lista de precios (resultados de scraping de varias URLs)
        prices = message
        
        # Filtra los precios válidos (excluye los no encontrados o los dominios no soportados)
        valid_prices = [(source, price, avail, promo, desc) for source, price, avail, promo, desc in prices if price != 'No encontrado' and price != 'Dominio no soportado']
        
        # Si hay precios válidos en la lista
        if valid_prices:
            # Encuentra el precio más bajo usando min(), eliminando comas y puntos del formato de precio para compararlo
            best_price = min(valid_prices, key=lambda x: float(x[1].replace(',', '').replace('.', '')))
            
            # Construye el resultado con el mejor precio, la disponibilidad, la promoción y una parte de la descripción (hasta 2000 caracteres)
            result = (
                f"Mejor precio: {best_price[1]} en {best_price[0]}\n"
                f"Disponibilidad: {best_price[2]}\n"
                f"Promoción: {best_price[3]}\n"
                f"Descripción: {best_price[4][:2000]}..."  # Limita la descripción a 2000 caracteres
            )
        else:
            # Si no se encontraron precios válidos, devuelve un mensaje indicándolo
            result = "No se encontraron precios válidos."

        # Envía el resultado al actor que solicitó la comparación
        self.send(sender, result)

#JOSE EL MEJOR PROFE  # Comentario que parece ser un saludo o reconocimiento a José :)

