import os
import json
import time
import pandas as pd
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from urllib.parse import urlparse
from dotenv import load_dotenv

# Configurar o logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(asctime)s - %(message)s')

# Carregar variáveis de ambiente
load_dotenv()

# Função para ler o arquivo JSON
def read_json_file(file_path):
    logging.info(f"Lendo o arquivo JSON de {file_path}")
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error(f"Arquivo não encontrado: {file_path}")
        raise
    except Exception as e:
        logging.error(f"Erro ao ler o arquivo JSON: {e}")
        raise

# Função para extrair o domínio final usando Selenium Grid com tentativas
def get_final_domain(url, retries=3, wait=15):
    selenium_grid_url = 'http://api.fulled.com.br:4444/wd/hub'
    chrome_options = Options()
    chrome_options.add_argument('--headless')

    for attempt in range(retries):
        logging.info(f"Tentativa {attempt + 1} de {retries} para URL: {url}")
        driver = webdriver.Remote(command_executor=selenium_grid_url, options=chrome_options)
        
        try:
            driver.get(url)
            time.sleep(5)
            final_url = driver.current_url
            parsed_url = urlparse(final_url)
            domain = parsed_url.netloc
            if domain.startswith("www."):
                domain = domain[4:]
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

# Função principal
def main():
    input_file = os.path.join(os.path.dirname(__file__), '..', '..', 'extracao', 'semanal', 'resultado_scrape', 'scrape_url.json')
    output_dir = os.path.join(os.path.dirname(__file__), 'resultado_trans')
    output_file = os.path.join(output_dir, 'url_final.json')
    
    # Ler o arquivo JSON
    data = read_json_file(input_file)
    
    # Criar DataFrame
    df = pd.DataFrame(data)
    logging.info("DataFrame criado com sucesso")
    
    # Extrair domínios finais
    df['url_final'] = df['url_visitada'].apply(lambda x: get_final_domain(x) if pd.notnull(x) else None)
    
    # Verificar se o diretório de saída existe, caso contrário, criar
    os.makedirs(output_dir, exist_ok=True)
    
    # Converter DataFrame para dicionário e salvar como JSON
    result = df.to_dict(orient='records')
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=4)
    
    logging.info(f"Arquivo JSON salvo com sucesso em {output_file}")

if __name__ == "__main__":
    main()
