#app.py
from flask import Flask, jsonify, request
import pandas as pd
from threading import Thread

app = Flask(__name__)
URL = "https://cbsnooper.com/reports/top-clickbank-products"

@app.route('/', methods=['GET'])
def index():
    return "<h1>App Ninja Click</h1>"

@app.route('/scrape', methods=['GET'])
def scrape_data():
    max_pages = request.args.get('max_pages', default=3, type=int)
    from login.login import login_to_cbsnooper_and_transfer_session
    from scrape.scrape import parse_all_pages_requests
    
    session = login_to_cbsnooper_and_transfer_session()

    def do_scrape():
        try:
            data, pages_processed = parse_all_pages_requests(session, URL, max_pages=max_pages)
            print(f"Total de páginas processadas: {pages_processed}")
            print(f"Total de produtos extraídos: {len(data)}")
            return data, pages_processed
        except Exception as e:
            print(f"Erro durante o scraping: {e}")
            return pd.DataFrame(), 0

    result_data, result_pages_processed = do_scrape()
    result = {
        'data': result_data.to_dict(orient='records'),
        'pages_processed': result_pages_processed,
        'products_count': len(result_data)
    }
    return jsonify(result)

if __name__ == '__main__':
    app.run()
