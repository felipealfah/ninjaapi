import os
import json
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client
import logging
import time
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

# Configurar o logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Função para remover o diretório __pycache__ se existir
def remover_pycache():
    pycache_path = os.path.join(os.getcwd(), '__pycache__')
    if os.path.exists(pycache_path):
        shutil.rmtree(pycache_path)
        logging.info("__pycache__ removido com sucesso.")
    else:
        logging.info("Nenhum diretório __pycache__ encontrado.")

# Carregar variáveis de ambiente
load_dotenv()
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_API_KEY = os.getenv('SUPABASE_API_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_API_KEY)

# Função para buscar todos os produtos onde id_plataforma é 1 e url_final está null, vazio, ou [null]
def fetch_products():
    response = (
        supabase.from_('produtos_fisicos')
        .select('id_produto, nome_produto, id_plataforma')
        .eq('id_plataforma', 1)
        .or_('url_final.is.null,url_final.eq.empty,url_final.eq.NULL,url_final.eq.[null]')
        .execute()
    )
    
    if response.data:
        logging.info("Produtos encontrados com url_final vazia ou nula:")
        print(response.data)  # Exibe os produtos encontrados
        return response.data
    else:
        logging.error(f"Erro ao buscar produtos: {response}")
        return []

# Função para criar um DataFrame com as URLs de scraping
def criar_dataframe_urls(produtos):
    dados = []

    for produto in produtos:
        id_produto = produto['id_produto']
        nome_produto = produto['nome_produto']
        url_scrape = f"https://cbsnooper.com/visit/{nome_produto}"
        
        dados.append({
            'id_produto': id_produto,
            'nome_produto': nome_produto,
            'url_scrape': url_scrape
        })
    
    df = pd.DataFrame(dados)
    return df

# Função para obter o domínio final a partir de uma URL
def get_final_domain(url, retries=3, wait=15):
    selenium_grid_url = 'http://api.fulled.com.br:4444'
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    
    for attempt in range(retries):
        logging.info(f"Tentativa {attempt + 1} de {retries} para URL: {url}")
        driver = webdriver.Remote(command_executor=selenium_grid_url, options=chrome_options)
        
        try:
            driver.get(url)
            time.sleep(5)  # Aguarda o carregamento da página
            final_url = driver.current_url  # Obtém a URL final
            parsed_url = urlparse(final_url)
            domain = parsed_url.netloc
            if domain.startswith("www."):
                domain = domain[4:]  # Remove "www."
            logging.info(f"Domínio final extraído: {domain}")
            return domain
        except WebDriverException as e:
            logging.error(f"Erro ao processar a URL {url}: {e}")
            if attempt < retries - 1:
                logging.info(f"Esperando {wait} segundos antes de tentar novamente...")
                time.sleep(wait)
        finally:
            driver.quit()
    
    logging.error(f"Falha ao processar a URL {url} após {retries} tentativas")
    return None

# Função principal para processar as URLs e registrar sucessos e falhas
def processar_urls(produtos_df):
    dados_url_final = []
    produtos_com_erro = []

    for _, row in produtos_df.iterrows():
        id_produto = row['id_produto']
        nome_produto = row['nome_produto']
        url_scrape = row['url_scrape']
        
        # Obtém o domínio final da URL
        domain = get_final_domain(url_scrape)
        
        if domain:
            dados_url_final.append({
                'id_produto': id_produto,
                'nome_produto': nome_produto,
                'url_scrape': url_scrape,
                'url_final': domain
            })
        else:
            produtos_com_erro.append({
                'id_produto': id_produto,
                'nome_produto': nome_produto,
                'url_scrape': url_scrape
            })
    
    # Cria o DataFrame final com os resultados de sucesso
    df_url_final = pd.DataFrame(dados_url_final)
    
    # Exibe o resumo de sucessos e falhas
    logging.info(f"Total de URLs extraídas com sucesso: {len(dados_url_final)}")
    logging.info(f"Total de URLs com erro: {len(produtos_com_erro)}")
    
    if produtos_com_erro:
        logging.warning("Produtos com erro na extração de URL:")
        for erro in produtos_com_erro:
            logging.warning(f"ID: {erro['id_produto']}, Nome: {erro['nome_produto']}, URL: {erro['url_scrape']}")
    
    return df_url_final

def executar_etl():
    produtos = fetch_products()
    if not produtos:
        logging.info("Nenhum produto encontrado para atualização.")
        return []

    df = criar_dataframe_urls(produtos)
    df_url_final = processar_urls(df)
    
    # Converte o DataFrame final em JSON e salva em um arquivo, substituindo se já existir
    json_result = df_url_final.to_dict(orient="records")
    json_filename = "scrape_url_final.json"

    # Verificar se o arquivo já existe e informar
    if os.path.exists(json_filename):
        logging.info(f"O arquivo {json_filename} já existe e será substituído.")
    
    with open(json_filename, "w") as json_file:
        json.dump(json_result, json_file, indent=4, ensure_ascii=False)
    
    logging.info("Processo ETL concluído com sucesso e resultado salvo em scrape_url_final.json.")
    return json_result

# Executa o processo ETL e gera o arquivo JSON
if __name__ == "__main__":
    resultado = executar_etl()
    print("Arquivo JSON gerado com sucesso.")


