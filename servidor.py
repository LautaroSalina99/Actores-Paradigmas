import argparse
import json
import socket
import time
import sched
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from thespian.actors import ActorSystem, Actor
from scrapers import scrape_mercadolibre, scrape_tiendamia, scrape_fullh4rd
from actors import ScraperActor, CompareActor

# Configuración de argumentos para modo cliente o servidor
parser = argparse.ArgumentParser(description="Modo de ejecución: Servidor o Cliente")
parser.add_argument('--mode', choices=['server', 'client'], required=True, help="Modo de ejecución: server o client")
args = parser.parse_args()

# Dirección y puerto del servidor
SERVER_IP = '172.16.12.42'
SERVER_PORT = 65432

def run_server():
    # Configuración del socket del servidor
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(5)
    print(f"Servidor escuchando en {SERVER_IP}:{SERVER_PORT}")

    def handle_client_connection(client_socket):
        while True:
            # Recibir el mensaje del cliente
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            
            try:
                # Convertir el mensaje de JSON a diccionario
                data = json.loads(message)
                print(f"Datos recibidos: {data}")
            except Exception as e:
                print(f"Error al procesar mensaje: {e}")

        client_socket.close()

    # Manejar conexiones entrantes
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Conexión establecida con {addr}")
        handle_client_connection(client_socket)

def run_client():
    # Conexión con el servidor
    def send_to_server(data):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((SERVER_IP, SERVER_PORT))
            message = json.dumps(data)
            client_socket.sendall(message.encode('utf-8'))
            print(f"Enviado al servidor: {data}")

    # Crear instancias de actores para scraping y comparación
    actor_system = ActorSystem()
    scraper_actors = []
    
    # Definir URLs de productos a comparar
    urls_Mouses = [
        'https://www.mercadolibre.com.ar/logitech-g-series-lightspeed-g502-negro/p/MLA15173180',
        'https://tiendamia.com/ar/producto?amz=B07L4BM851&pName=Logitech%20G502%20Lightspeed%20Wireless%20Gaming%20Mouse%20with%20Hero%2025K%20Sensor&comma;%20PowerPlay%20Compatible&comma;%20Tunable%20Weights%20and%20Lightsync%20RGB%20-%20Black',
        'https://fullh4rd.com.ar/prod/12631/mouse-logitech-g502-wireless-gaming-lightspeed-910-005566',
    ]

    # Crear actores para cada URL de scraping
    for url in urls_Mouses:
        scraper_actors.append(actor_system.createActor(ScraperActor))

    compare_actor = actor_system.createActor(CompareActor)

    # Función para hacer el scraping y enviar resultados al servidor
    def perform_scraping_and_send():
        prices = [(actor_system.ask(scraper, url, 10)) for scraper, url in zip(scraper_actors, urls_Mouses)]
        # Enviar los resultados al actor de comparación
        best_price = actor_system.ask(compare_actor, prices, 10)
        # Enviar al servidor el resultado final
        send_to_server(best_price)
    
    # Programar la búsqueda de precios cada 30 segundos
    scheduler = sched.scheduler(time.time, time.sleep)
    
    def schedule_scraping(scheduler):
        perform_scraping_and_send()
        scheduler.enter(30, 1, schedule_scraping, (scheduler,))
    
    scheduler.enter(0, 1, schedule_scraping, (scheduler,))
    scheduler.run()

# Ejecutar según el modo especificado
if args.mode == 'server':
    run_server()
elif args.mode == 'client':
    run_client()
