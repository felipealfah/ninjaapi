# app.py
from flask import Flask, jsonify, request
import pandas as pd
from threading import Thread
from queue import Queue

app = Flask(__name__)
URL = "https://cbsnooper.com/reports/top-clickbank-products"

@app.route('/', methods=['GET'])
def index():
    return "<h1>App Ninja Click</h1>"

def scrape_in_background(session, URL, queue):
    from scrape.scrape import parse_all_pages_requests
    try:
        data, pages_processed = parse_all_pages_requests(session, URL)
        print(f"Total de páginas processadas: {pages_processed}")
        print(f"Total de produtos extraídos: {len(data)}")
        queue.put((data, pages_processed))
    except Exception as e:
        print(f"Erro durante o scraping: {e}")
        queue.put((pd.DataFrame(), 0))

@app.route('/scrape', methods=['GET'])
def scrape_data():
    from login.login import login_to_cbsnooper_and_transfer_session
    
    session = login_to_cbsnooper_and_transfer_session()
    
    result_queue = Queue()
    thread = Thread(target=scrape_in_background, args=(session, URL, result_queue))
    thread.start()
    thread.join()  # This will wait for the thread to complete
    
    data, pages_processed = result_queue.get()  # Get the result from the queue
    result = {
        'data': data.to_dict(orient='records'),
        'pages_processed': pages_processed,
        'products_count': len(data)
    }
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
