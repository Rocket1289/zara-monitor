import time
from flask import Flask
from threading import Thread
import logging
import requests
import os

logging.basicConfig(level=logging.INFO)
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

def send_notification(is_available=False):
    try:
        if is_available:
            title = "🟢 Płaszcz dostępny!"
            message = f"Rozmiar M jest dostępny!\n{URL}"
        else:
            title = "🔄 Test monitora"
            message = "Monitor działa prawidłowo"

        response = requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=message,
            headers={
                "Title": title,
                "Priority": "urgent",
                "Tags": "shopping_cart"
            }
        )
        logger.info(f"Status powiadomienia ntfy: {response.status_code}")
    except Exception as e:
        logger.error(f"Błąd wysyłania ntfy: {str(e)}")

def check_availability():
    logger.info("Sprawdzam dostępność...")
    # Na razie wysyłamy testowe powiadomienie
    send_notification(is_available=False)

def run_checker():
    while True:
        check_availability()
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    Thread(target=run_checker, daemon=True).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
