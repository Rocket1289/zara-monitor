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
        # Używamy allorigins.win jako proxy
        proxy_url = f"https://api.allorigins.win/raw?url={URL}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pl,en-US;q=0.9,en;q=0.8'
        }
        
        logger.debug(f"Sprawdzam URL przez proxy: {proxy_url}")
        response = requests.get(proxy_url, headers=headers, timeout=30)
        logger.info(f"Status odpowiedzi: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Logujemy fragment strony do analizy
            logger.debug(f"Fragment strony: {response.text[:1000]}")
            
            text = soup.get_text().upper()
            logger.debug(f"Fragment tekstu: {text[:500]}")
            
            # Sprawdzamy dostępność
            if "BRAK DOSTĘPNOŚCI" not in text and ("ROZMIAR M" in text or "SIZE M" in text):
                logger.info("Rozmiar M może być dostępny! Wysyłam powiadomienie.")
                send_notification(is_available=True)
            else:
                logger.info("Rozmiar M niedostępny lub nie znaleziono informacji")
            
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
