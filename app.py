from flask import Flask, jsonify, request
from threading import Thread
import pandas as pd

# Importe o seu módulo de scraping
from .login import login_to_cbsnooper_and_transfer_session
from .scraper import parse_all_pages_requests  # Asumindo que seu código está em scraper.py

app = Flask(__name__)

# Configuração do login (placeholder)
session = login_to_cbsnooper_and_transfer_session()

@app.route('/scrape', methods=['GET'])
def scrape_data():
    # Argumento opcional para limitar o número de páginas raspadas
    max_pages = request.args.get('max_pages', default=3, type=int)
    
    # Processamento em uma thread separada para evitar bloquear o servidor
    def do_scrape():
        global data
        try:
            # Utilize a sessão global e o URL definido
            data = parse_all_pages_requests(session, URL, max_pages=max_pages)
        except Exception as e:
            print(f"Erro durante o scraping: {e}")
            data = pd.DataFrame()

    thread = Thread(target=do_scrape)
    thread.start()
    thread.join()  # Aguarde a thread terminar para garantir que os dados estão prontos
    
    # Converter DataFrame para JSON
    return jsonify(data.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
