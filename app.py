from flask import Flask, jsonify, request
from threading import Thread
import pandas as pd

# Importe o seu módulo de scraping
from login.login import login_to_cbsnooper_and_transfer_session
from scrape.scrape import parse_all_pages_requests  # Asumindo que seu código está em scraper.py

app = Flask(__name__)

# Configuração do login (placeholder)
session = login_to_cbsnooper_and_transfer_session()
URL = "https://cbsnooper.com/reports/top-clickbank-products"

@app.route('/scrape', methods=['GET'])
def scrape_data():
    max_pages = request.args.get('max_pages', default=3, type=int)
    
    def do_scrape():
        global data, pages_processed
        try:
            data, pages_processed = parse_all_pages_requests(session, URL, max_pages=max_pages)
            print(f"Total de páginas processadas: {pages_processed}")
            print(f"Total de produtos extraídos: {len(data)}")
        except Exception as e:
            print(f"Erro durante o scraping: {e}")
            data = pd.DataFrame()
            pages_processed = 0

    thread = Thread(target=do_scrape)
    thread.start()
    thread.join()
    
    result = {
        'data': data.to_dict(orient='records'),
        'pages_processed': pages_processed,
        'products_count': len(data)
    }
    return jsonify(result)

if __name__ == '__main__':
    app.run
