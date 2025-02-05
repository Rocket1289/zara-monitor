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
        # Używamy API mobilnego Zary
        api_url = "https://www.zara.com/itxrest/2/catalog/store/24009401/40259520/product/05854004/detail"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
            'Accept': 'application/json',
            'Accept-Language': 'pl-PL;q=1.0',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        logger.debug(f"Sprawdzam API mobilne: {api_url}")
        response = requests.get(api_url, headers=headers, timeout=30)
        logger.info(f"Status odpowiedzi: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logger.debug(f"Odpowiedź API: {data}")
            
            sizes = data.get('detail', {}).get('sizes', [])
            for size in sizes:
                if size.get('name') == 'M' and size.get('availability'):
                    logger.info("Rozmiar M dostępny! Wysyłam powiadomienie.")
                    send_notification(is_available=True)
                    return
                    
            logger.info("Rozmiar M niedostępny")
            
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
