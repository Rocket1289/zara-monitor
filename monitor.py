def check_availability():
    try:
        # Nowy endpoint API Zary
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
            
            # Logujemy całą odpowiedź do analizy struktury
            logger.debug(f"Pełna odpowiedź: {response.text[:1000]}")
            
            # Na razie nie sprawdzamy dostępności - zobaczymy co zwraca API
            logger.info("Otrzymano odpowiedź z API - sprawdzam format danych")
            
    except Exception as e:
        logger.error(f"Nieoczekiwany błąd: {str(e)}")
