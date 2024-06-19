import os
import json
import pandas as pd
import requests
import logging
from dotenv import load_dotenv
from supabase import create_client, Client

# Configurar o logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Carregar variáveis de ambiente
load_dotenv()
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_API_KEY = os.getenv('SUPABASE_API_KEY')
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')
RAPIDAPI_HOST = os.getenv('RAPIDAPI_HOST')

supabase = create_client(SUPABASE_URL, SUPABASE_API_KEY)

# Função para buscar produtos
def fetch_products():
    response = supabase.from_('produtos_fisicos').select('id_produto, nome_produto, url_final').execute()
    if response.data:
        return response.data
    else:
        logging.error(f"Erro ao buscar produtos: {response.error}")
        return []

# Função para obter dados de tráfego
def get_traffic_data(domain):
    url = "https://similarweb12.p.rapidapi.com/v2/website-analytics/"
    querystring = {"domain": domain}

    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }
    
    attempts = 0
    max_attempts = 3
    
    while attempts < max_attempts:
        try:
            response = requests.get(url, headers=headers, params=querystring)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 404:
                logging.error(f"Domínio não encontrado: {domain} - {http_err}")
                break  # Não tentar novamente se o domínio não for encontrado
            else:
                logging.error(f"Erro HTTP ao obter dados de tráfego para {domain}: {http_err}")
        except requests.RequestException as e:
            logging.error(f"Erro ao obter dados de tráfego para {domain}: {e}")
        
        attempts += 1
        logging.info(f"Tentativa {attempts} de {max_attempts} falhou para {domain}. Tentando novamente...")

    return None

# Função principal
def main():
    data = fetch_products()

    # Criar DataFrame
    df = pd.DataFrame(data)

    # Adicionar colunas vazias ao DataFrame
    df["mes_atual"] = None
    df["mes_anterior"] = None
    df["dois_meses"] = None
    df["pais1"] = None
    df["pais2"] = None
    df["pais3"] = None
    df["pais4"] = None
    df["pais5"] = None

    # Processar cada domínio e atualizar o DataFrame
    for index, row in df.iterrows():
        domain = row["url_final"]
        if pd.notnull(domain):
            logging.info(f"Obtendo dados de tráfego para {domain}")
            data = get_traffic_data(domain)
            if data:
                try:
                    traffic = data.get("traffic", {})
                    geography = data.get("geography", {})
                    history = traffic.get("history", [])
                    top_countries = geography.get("topCountriesTraffics", [])

                    # Atualizar os dados de tráfego no DataFrame
                    df.at[index, "mes_atual"] = history[2]["visits"] if len(history) > 2 else None
                    df.at[index, "mes_anterior"] = history[1]["visits"] if len(history) > 1 else None
                    df.at[index, "dois_meses"] = history[0]["visits"] if len(history) > 0 else None

                    # Atualizar os países no DataFrame
                    df.at[index, "pais1"] = top_countries[0]["countryUrlCode"] if len(top_countries) > 0 else None
                    df.at[index, "pais2"] = top_countries[1]["countryUrlCode"] if len(top_countries) > 1 else None
                    df.at[index, "pais3"] = top_countries[2]["countryUrlCode"] if len(top_countries) > 2 else None
                    df.at[index, "pais4"] = top_countries[3]["countryUrlCode"] if len(top_countries) > 3 else None
                    df.at[index, "pais5"] = top_countries[4]["countryUrlCode"] if len(top_countries) > 4 else None

                except (KeyError, IndexError) as e:
                    logging.error(f"Erro ao processar dados de tráfego para {domain}: {e}")

    # Verificar se o diretório de saída existe, caso contrário, criar
    output_dir = os.path.join(os.path.dirname(__file__), 'resultado_quinze')
    os.makedirs(output_dir, exist_ok=True)

    # Salvar o DataFrame como JSON
    output_file = os.path.join(output_dir, 'trans_trafego.json')
    df.to_json(output_file, orient='records', indent=4)

    logging.info(f"Arquivo JSON salvo com sucesso em {output_file}")

if __name__ == "__main__":
    main()
