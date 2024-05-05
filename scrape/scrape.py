# scrape.py
from bs4 import BeautifulSoup
import httpx
import asyncio
import random

async def extract_url_from_onclick(onclick_value):
    start = onclick_value.find("('") + 2
    end = onclick_value.find("',", start)
    return onclick_value[start:end]

def exponential_backoff_with_jitter(attempt, max_delay=60):
    base = 2 ** attempt
    jitter = random.uniform(0, 1) * base * 0.1  # 10% jitter
    delay = min(max_delay, base + jitter)
    return delay

async def parse_data_requests_with_retry(client, url, max_retries=3):
    products = []  # Inicializa a lista de produtos
    for attempt in range(max_retries):
        try:
            response = await client.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')  # Usando lxml para parsing
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
                return products
            else:
                print(f"Nenhum produto encontrado na página {url}.")
        except httpx.RequestError as e:
            print(f"Erro de rede na tentativa {attempt + 1}: {e}")
            await asyncio.sleep(exponential_backoff_with_jitter(attempt))
        except Exception as e:
            print(f"Erro no processamento na tentativa {attempt + 1}: {e}")
            await asyncio.sleep(exponential_backoff_with_jitter(attempt))

    print("Todas as tentativas falharam.")
    return []

async def parse_all_pages_requests(client, base_url):
    all_products = []
    page_number = 1
    while True:
        current_url = f"{base_url}?page={page_number}"
        print(f"Processando página {page_number}...")
        current_page_products = await parse_data_requests_with_retry(client, current_url)
        if current_page_products:
            all_products.extend(current_page_products)
            print(f"Produtos inseridos na lista até o momento: {len(all_products)}")
            page_number += 1
        else:
            print(f"Nenhum produto encontrado na página {page_number}, terminando a extração.")
            break
    return all_products, page_number - 1  # Agora retorna o número de páginas processadas
