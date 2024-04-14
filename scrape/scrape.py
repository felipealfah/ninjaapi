from login.login import login_to_cbsnooper_and_transfer_session
from bs4 import BeautifulSoup
import pandas as pd
import requests
import time

import sys
import os

URL = "https://cbsnooper.com/reports/top-clickbank-products"

def extract_url_from_onclick(onclick_value):
    start = onclick_value.find("('") + 2
    end = onclick_value.find("',", start)
    return onclick_value[start:end]

def parse_data_requests_with_retry(session, url, max_retries=3, sleep_interval=10):
    for attempt in range(max_retries):
        try:
            response = session.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                table = soup.find("table")
                if not table:
                    raise ValueError("Tabela não encontrada na página.")
                
                products = []
                rows = table.find_all("tr")[1:]
                for row in rows:
                    cells = row.find_all("td")
                    if cells:
                        onclick_value = cells[1].get('onclick', '')
                        link_cb = extract_url_from_onclick(onclick_value) if onclick_value else ''

                        # Formatação de Gravity para remover pontos
                        gravity = cells[3].text.strip().replace('.', '')
                        # Formatação do Mov_Diario para remover pontos
                        mov_diario = cells[4].text.strip().replace('.', '')
                        # Formatação do Preço para remover o símbolo de dólar e pontos, substituindo vírgula por ponto
                        preco = cells[6].text.strip().replace('$', '')

                        product = {
                            "Ranking": cells[0].text.strip(),
                            "Nome": cells[1].text.strip(),
                            "Descricao": cells[2].text.strip(),
                            "GravityDia": gravity,
                            "Mov_Diario": mov_diario,
                            "Preco": preco,
                            "link_cb": link_cb
                        }
                        products.append(product)

                return pd.DataFrame(products)
        except Exception as e:
            print(f"Erro na tentativa {attempt + 1}: {e}. Tentando novamente em {sleep_interval} segundos.")
            time.sleep(sleep_interval)
    
    print("Todas as tentativas falharam.")
    return pd.DataFrame()

#def parse_all_pages_requests(session, base_url):
def parse_all_pages_requests(session, base_url, max_pages=3):
    all_products = pd.DataFrame()
    page_number = 1
    pages_processed = 0  # Contador para as páginas processadas
    #while True:
    while page_number <= max_pages:
        current_url = f"{base_url}?page={page_number}"
        print(f"Processando página {page_number}...")
        current_page_products = parse_data_requests_with_retry(session, current_url)
        if current_page_products.empty:
            print(f"Nenhum produto encontrado na página {page_number}, terminando a extração.")
            break
        all_products = pd.concat([all_products, current_page_products], ignore_index=True)
        pages_processed += 1
        page_number += 1

    return all_products, pages_processed