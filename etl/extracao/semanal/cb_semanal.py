import os
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Carregar variáveis de ambiente
load_dotenv()
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_API_KEY = os.getenv('SUPABASE_API_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_API_KEY)

# Função para puxar os registros da tabela produtos
def fetch_products():
    response = supabase.from_('produtos_fisicos').select('nome_produto, url_produto, url_afiliado').execute()
    if response.data:
        return response.data
    else:
        logging.error(f"Erro ao buscar produtos: {response.error}")
        return []

# Função para fazer o scraping do link de afiliado
def scrape_affiliate_link(url, nome_produto):
    try:
        logging.info(f"Iniciando scraping para o produto: {nome_produto}, URL: {url}")
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            affiliate_link = soup.find('a', {'class': 'text-blue-800 bg-transparent border border-blue-800 hover:bg-blue-900 hover:text-white focus:ring-4 focus:outline-none focus:ring-blue-200 font-medium rounded-lg text-xs px-3 py-1.5 mr-2 text-center dark:hover:bg-blue-600 dark:border-blue-600 dark:text-blue-400 dark:hover:text-white dark:focus:ring-blue-800'})['href']
            logging.info(f"Link de afiliado extraído para o produto {nome_produto}: {affiliate_link}")
            return affiliate_link
        else:
            logging.error(f"Erro ao acessar URL {url}: Status code {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"Erro ao fazer scraping do link de afiliado para o produto {nome_produto} em {url}: {e}")
        return None

# Função principal
def main():
    # Puxar os produtos
    produtos = fetch_products()
    
    # Criar DataFrame
    df = pd.DataFrame(produtos)
    
    # Preencher a coluna url_produto
    df['url_produto'] = df['nome_produto'].apply(lambda x: f'https://cbsnooper.com/products/{x}')
    
    # Fazer o scraping dos links de afiliado
    df['url_afiliado'] = df.apply(lambda row: scrape_affiliate_link(row['url_produto'], row['nome_produto']), axis=1)
    
    # Gerar JSON e salvar
    result = df.to_dict(orient='records')
    output_dir = 'etl/extracao/semanal/resultado_scrape'
    output_file = f'{output_dir}/cb_scrape_semanal.json'
    
    os.makedirs(output_dir, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=4)
    
    logging.info(f"Arquivo JSON salvo com sucesso em {output_file}")

# Executar a função principal
if __name__ == "__main__":
    main()
