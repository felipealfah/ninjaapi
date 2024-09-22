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

# Função para puxar os registros da tabela produtos com plataforma específica
def fetch_products():
    response = supabase.from_('produtos_fisicos').select('nome_produto, url_produto, url_afiliado').eq('id_plataforma', 1).execute()
    if response.data:
        return response.data
    else:
        logging.error(f"Erro ao buscar produtos: {response.error}")
        return []

# Função para fazer o scraping do link de afiliado e da data "First seen"
def scrape_product_data(url, nome_produto):
    try:
        logging.info(f"Iniciando scraping para o produto: {nome_produto}, URL: {url}")
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraindo o link de afiliado
            affiliate_link = soup.find('a', {'class': 'text-blue-800 bg-transparent border border-blue-800 hover:bg-blue-900 hover:text-white focus:ring-4 focus:outline-none focus:ring-blue-200 font-medium rounded-lg text-xs px-3 py-1.5 mr-2 text-center dark:hover:bg-blue-600 dark:border-blue-600 dark:text-blue-400 dark:hover:text-white dark:focus:ring-blue-800'})
            affiliate_link = affiliate_link['href'] if affiliate_link else None
            
            # Extraindo a data de 'First seen'
            first_seen_element = soup.find('span', {'class': 'font-bold mb-4 text-gray-500 dark:text-white'})
            first_seen_date = first_seen_element.text.replace('First seen ', '').strip() if first_seen_element else None
            
            logging.info(f"Link de afiliado extraído para o produto {nome_produto}: {affiliate_link}")
            logging.info(f"Data de 'First seen' extraída para o produto {nome_produto}: {first_seen_date}")
            
            return affiliate_link, first_seen_date
        else:
            logging.error(f"Erro ao acessar URL {url}: Status code {response.status_code}")
            return None, None
    except Exception as e:
        logging.error(f"Erro ao fazer scraping dos dados para o produto {nome_produto} em {url}: {e}")
        return None, None

# Função principal
def main():
    # Puxar os produtos
    produtos = fetch_products()
    
    # Criar DataFrame
    df = pd.DataFrame(produtos)
    
    # Preencher a coluna url_produto
    df['url_produto'] = df['nome_produto'].apply(lambda x: f'https://cbsnooper.com/products/{x}')
    
    # Fazer o scraping dos links de afiliado e da data "First seen"
    df['url_afiliado'], df['first_seen_date'] = zip(*df.apply(lambda row: scrape_product_data(row['url_produto'], row['nome_produto']), axis=1))
    
    # Gerar JSON e salvar
    result = df.to_dict(orient='records')
    
    # Corrigir o caminho do diretório de saída
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, '..', '..', 'extracao', 'semanal', 'resultado_scrape')
    output_file = os.path.join(output_dir, 'cb_scrape_semanal.json')
    
    os.makedirs(output_dir, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=4)
    
    logging.info(f"Arquivo JSON salvo com sucesso em {output_file}")

# Executar a função principal
if __name__ == "__main__":
    main()
