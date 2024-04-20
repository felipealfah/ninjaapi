# scrape.py
from login.login import login_to_cbsnooper_and_transfer_session
from bs4 import BeautifulSoup
import pandas as pd
import requests
import time
import random

URL = "https://cbsnooper.com/reports/top-clickbank-products"

def extract_url_from_onclick(onclick_value):
    start = onclick_value.find("('") + 2
    end = onclick_value.find("',", start)
    return onclick_value[start:end]

def exponential_backoff(attempt):
    # Define um máximo de espera de 60 segundos e adiciona um componente aleatório.
    return min(60, (2 ** attempt) + random.randint(0, 1000) / 1000)

def parse_data_requests_with_retry(session, url, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = session.get(url)
            response.raise_for_status()  # Garante que erros HTTP sejam tratados como exceções.
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

                    gravity = cells[3].text.strip().replace('.', '')
                    mov_diario = cells[4].text.strip().replace('.', '')
                    preco = cells[6].text.strip().replace('$', '').replace(',', '.')

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
        except requests.exceptions.RequestException as e:
            print(f"Erro de rede na tentativa {attempt + 1}: {e}")
            time.sleep(exponential_backoff(attempt))
        except Exception as e:
            print(f"Erro no processamento na tentativa {attempt + 1}: {e}")
            time.sleep(exponential_backoff(attempt))

    print("Todas as tentativas falharam.")
    return pd.DataFrame()

def parse_all_pages_requests(session, base_url, max_pages=3):
    all_products = pd.DataFrame()
    page_number = 1
    pages_processed = 0  # Contador para as páginas processadas
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

# O código abaixo pode ser removido ou comentado se o script for chamado/importado de outro lugar
# Realiza o login e obtém a sessão
session = login_to_cbsnooper_and_transfer_session()
if session:
    products, pages_processed = parse_all_pages_requests(session, URL)
    print(f"Extração concluída. {pages_processed} páginas processadas.")
else:
    print("Falha ao obter a sessão de login.")
