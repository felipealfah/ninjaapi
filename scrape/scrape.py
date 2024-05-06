import asyncio
from bs4 import BeautifulSoup
import httpx
import random
import json
from datetime import datetime
import logging

# URL base para scraping
URL = "https://cbsnooper.com/reports/top-clickbank-products"

# Configuração de Logging
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

setup_logging()

# Função para extrair URL de onclick
async def extract_url_from_onclick(onclick_value):
    start = onclick_value.find("('") + 2
    end = onclick_value.find("',", start)
    return onclick_value[start:end]

# Função para implementar backoff exponencial com jitter
def exponential_backoff_with_jitter(attempt, max_delay=60):
    base = 2 ** attempt
    jitter = random.uniform(0, 1) * base * 0.1
    delay = min(max_delay, base + jitter)
    return delay

# Função para parsear dados da página com retries
async def parse_data_requests_with_retry(client, url, max_retries=3):
    products = []
    for attempt in range(max_retries):
        try:
            response = await client.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            table = soup.find("table")
            if not table:
                raise ValueError("Tabela não encontrada na página.")
            rows = table.find_all("tr")[1:]
            for row in rows:
                cells = row.find_all("td")
                if cells and len(cells) >= 7:
                    onclick_value = cells[1].get('onclick', '')
                    link_cb = await extract_url_from_onclick(onclick_value) if onclick_value else ''
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
            if products:
                logging.info(f"Produtos coletados da página {url}.")
                return products
            else:
                logging.info(f"Nenhum produto encontrado na página {url}.")
        except httpx.RequestError as e:
            logging.error(f"Erro de rede na tentativa {attempt + 1}: {e}")
            await asyncio.sleep(exponential_backoff_with_jitter(attempt))
        except Exception as e:
            logging.error(f"Erro no processamento na tentativa {attempt + 1}: {e}")
            await asyncio.sleep(exponential_backoff_with_jitter(attempt))
    logging.warning("Todas as tentativas falharam.")
    return []

# Função para extrair todos os produtos de todas as páginas
async def parse_all_pages_requests(client, base_url):
    all_products = []
    page_number = 1
    while True:
        current_url = f"{base_url}?page={page_number}"
        print(f"Processando página {page_number}...")
        products = await parse_data_requests_with_retry(client, current_url)
        if not products:
            print(f"Nenhum produto encontrado na página {page_number}, terminando a extração.")
            break
        all_products.extend(products)
        page_number += 1
    return all_products

# Função para salvar produtos em JSON
def save_to_json(products, filename="resultado_scrape.json"):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data_with_timestamp = {
        "generated_on": current_time,
        "products": products
    }
    with open(filename, 'w') as f:
        json.dump(data_with_timestamp, f, indent=4)
        logging.info(f"Dados salvos com sucesso em {filename}")

# Execução principal para teste
async def main():
    async with httpx.AsyncClient() as client:
        products = await parse_all_pages_requests(client, URL, max_pages=5)  # Ajuste o número de páginas conforme necessário
        if products:
            save_to_json(products)
        else:
            logging.info("Nenhum produto foi encontrado para salvar.")

if __name__ == "__main__":
    asyncio.run(main())
