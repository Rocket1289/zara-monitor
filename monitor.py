import time
from flask import Flask
from threading import Thread
import logging
import requests
import os
import json

logging.basicConfig(
    level=logging.DEBUG,  # Zmienione na DEBUG dla lepszego logowania
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PRODUCT_ID = "05854004"
URL = "https://www.zara.com/pl/pl/p%C5%82aszcz-o-strukturze-w-jode%C5%82ke-z-we%C5%82na-p05854004.html?v1=402490876"
NTFY_TOPIC = "zara-monitor-rocket128"
CHECK_INTERVAL = 600

app = Flask(__name__)

@app.route('/')
def home():
    return "Monitor dziala!"

@app.route('/ping')
def ping():
    logger.info("Ping otrzymany")
    return "pong"

@app.route('/test_ntfy')
def test_ntfy():
    """Endpoint do testowania powiadomień"""
    send_notification(is_available=True)
    return "Notification sent"

def send_notification(is_available=False):
    try:
        if is_available:
            title = "Płaszcz dostępny!"
            message = f"Rozmiar M jest dostępny!\n{URL}"

            response = requests.post(
                f"https://ntfy.sh/{NTFY_TOPIC}",
                data=message.encode('utf-8'),
                headers={
                    "Title": title,
                    "Priority": "urgent",
                    "Tags": "shopping_cart"
                }
            )
            response.raise_for_status()  # Sprawdza błędy HTTP
            logger.info(f"Status powiadomienia ntfy: {response.status_code}")
    except Exception as e:
        logger.error(f"Błąd wysyłania ntfy: {str(e)}")

def check_availability():
    try:
        api_url = f"https://www.zara.com/pl/pl/products/{PRODUCT_ID}/stock"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'pl,en-US;q=0.9,en;q=0.8',
            'Referer': URL,
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        
        logger.debug(f"Sprawdzam URL: {api_url}")
        response = requests.get(api_url, headers=headers, timeout=30)
        logger.info(f"Status odpowiedzi: {response.status_code}")
        
        # Logujemy nagłówki odpowiedzi
        logger.debug(f"Otrzymane nagłówki: {dict(response.headers)}")
        
        response.raise_for_status()
        
        try:
            data = response.json()
            # Logujemy całą odpowiedź JSON do analizy
            logger.debug(f"Odpowiedź API: {json.dumps(data, indent=2)}")
            
            sizes = data.get('sizes', [])
            if not sizes:
                logger.warning("Brak informacji o rozmiarach w odpowiedzi")
                return
                
            for size in sizes:
                # Logujemy każdy rozmiar do analizy
                logger.debug(f"Sprawdzam rozmiar: {size}")
                if size.get('name') == 'M' and size.get('availability') == 'in_stock':
                    logger.info("Rozmiar M dostępny! Wysyłam powiadomienie.")
                    send_notification(is_available=True)
                    return
                    
            logger.info("Rozmiar M niedostępny")
            
        except json.JSONDecodeError:
            logger.error("Nieprawidłowy format JSON w odpowiedzi")
            logger.debug(f"Treść odpowiedzi: {response.text[:500]}")
            
    except requests.exceptions.HTTPError as e:
        logger.error(f"Błąd HTTP: {e.response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Błąd połączenia: {str(e)}")
    except Exception as e:
        logger.error(f"Nieoczekiwany błąd: {str(e)}")

def run_checker():
    while True:
        check_availability()
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    Thread(target=run_checker, daemon=True).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
