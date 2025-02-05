import time
from flask import Flask
from threading import Thread
import logging
import requests
import os
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.DEBUG)
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

def send_notification():
    try:
        message = f"Mozliwe ze rozmiar M jest dostepny! Sprawdz:\n{URL}"
        
        response = requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=message.encode('utf-8'),
            headers={
                "Title": "Sprawdz dostepnosc!",
                "Priority": "urgent",
                "Tags": "shopping_cart"
            }
        )
        logger.info(f"Status powiadomienia: {response.status_code}")
    except Exception as e:
        logger.error(f"Blad wysylania powiadomienia: {e}")

def check_availability():
    try:
        # Używamy API Instakartu
        api_url = "https://www.instacart.com/store/zara/product/5854004"
        
        headers = {
            'User-Agent': 'Instacart/1.0',
            'Accept': 'application/json',
            'Origin': 'https://www.instacart.com'
        }

        response = requests.get(api_url, headers=headers, timeout=30)
        logger.info(f"Status odpowiedzi: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            sizes = data.get('variants', [])
            
            for size in sizes:
                if size.get('size') == 'M' and size.get('available'):
                    logger.info("Rozmiar M dostepny!")
                    send_notification()
                    return
                    
            logger.info("Rozmiar M niedostepny")
    except Exception as e:
        logger.error(f"Blad podczas sprawdzania: {e}")

def run_checker():
    while True:
        check_availability()
        time.sleep(CHECK_INTERVAL)

app.config['port'] = int(os.environ.get('PORT', 10000))
Thread(target=run_checker, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=app.config['port'])
