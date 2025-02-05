import time
from flask import Flask
from threading import Thread
import logging
import requests
import os
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
            response.raise_for_status()
            logger.info(f"Status powiadomienia ntfy: {response.status_code}")
    except Exception as e:
        logger.error(f"Błąd wysyłania ntfy: {str(e)}")

def check_availability():
    try:
        api_url = "https://www.zara.com/pl/pl/shop/product-details"
        
        headers = {
            'User-Agent': 'ZaraApp',
            'Accept': 'application/json',
            'Accept-Language': 'pl-PL',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': URL
        }
        
        params = {
            'productId': '05854004',
            'ajax': 'true'
        }
        
        logger.debug(f"Sprawdzam API produktu: {api_url}")
        response = requests.get(api_url, headers=headers, params=params, timeout=30)
        logger.info(f"Status odpowiedzi: {response.status_code}")
        logger.debug(f"Nagłówki odpowiedzi: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            logger.debug(f"Odpowiedź API: {data}")
            logger.debug(f"Pełna odpowiedź: {response.text[:1000]}")
            logger.info("Otrzymano odpowiedź z API - sprawdzam format danych")
            
    except Exception as e:
        logger.error(f"Nieoczekiwany błąd: {str(e)}")

def run_checker():
    while True:
        check_availability()
        time.sleep(CHECK_INTERVAL)

# Ustawienia portu dla Render.com
app.config['port'] = int(os.environ.get('PORT', 10000))

# Uruchamiamy wątek sprawdzający
Thread(target=run_checker, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=app.config['port'])
