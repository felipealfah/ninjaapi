from dotenv import load_dotenv
import os
import json
import pandas as pd
from supabase import create_client, Client
from datetime import datetime
from urllib.parse import urlparse
import logging

# Carregar variáveis de ambiente
load_dotenv()
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_API_KEY = os.getenv('SUPABASE_API_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_API_KEY)

# Configuração do logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Função para ler o arquivo JSON
def read_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error(f'Arquivo JSON não encontrado: {file_path}')
        raise
    except json.JSONDecodeError:
        logger.error(f'Erro ao decodificar o JSON do arquivo: {file_path}')
        raise

# Função para transformar os dados em um DataFrame
def transform_data(data):
    produtos = data.get("produtos", [])
    if not produtos:
        logger.warning("Nenhum produto encontrado no JSON.")
    
    # Criar DataFrame
    df = pd.DataFrame(produtos)

    # Verificar e adicionar colunas faltantes
    required_columns = {
        "title": "nome_produto",
        "description": "desc_produto",
        "average_payout": "preco_comissao",
        "product_link": "url_produto",
        "conversion_rate": "conversao",
        "allowed_geos": "localidades",
        "restrictions": "restricoes",
    }

    for col in required_columns:
        if col not in df.columns:
            logger.warning(f"Coluna ausente no DataFrame: {col}")

    # Renomear colunas conforme necessário
    df = df.rename(columns=required_columns)

    # Validar e converter tipos de dados
    df["preco_comissao"] = pd.to_numeric(df["preco_comissao"].str.replace("$", ""), errors='coerce')
    df["conversao"] = pd.to_numeric(df["conversao"].str.replace("%", ""), errors='coerce')

    # Tratar a coluna 'data' e converter para datetime
    df["data"] = pd.to_datetime(data.get("data_criacao", datetime.now().isoformat()), format='%Y-%m-%d %H:%M:%S', errors='coerce')

    # Validação de dados
    df = df.dropna(subset=["nome_produto", "url_produto", "preco_comissao"])

    return df

# Função para extrair o domínio de uma URL
def extract_domain(url):
    if not url:
        return "null"
    parsed_url = urlparse(url)
    return parsed_url.netloc

# Função para verificar se o produto existe e inserir/atualizar dados
def upsert_data(file_path):
    try:
        data = read_json_file(file_path)
        df = transform_data(data)

        for index, row in df.iterrows():
            nome_produto = row["nome_produto"]
            url_final = extract_domain(row["url_produto"])

            # Verificar se o produto já existe na tabela produtos_fisicos
            response = supabase.from_('produtos_fisicos').select('id_produto').eq('nome_produto', nome_produto).execute()
            if response.data:
                id_produto = response.data[0]['id_produto']
                logger.info(f"Produto {nome_produto} já existe com id {id_produto}. Atualizando dados.")

                # Atualizar produto existente na tabela produtos_fisicos
                supabase.from_('produtos_fisicos').update({
                    "url_produto": row["url_produto"],
                    "url_final": url_final,
                    "preco_comissao": row["preco_comissao"],
                    "desc_produto": row["desc_produto"]
                }).eq('id_produto', id_produto).execute()

                # Inserir novo registro em bg_fisico
                bg_fisico_data = {
                    "id_produto": id_produto,
                    "data": row["data"].strftime('%Y-%m-%d'),
                    "localidades": row["localidades"],
                    "restricoes": row["restricoes"],
                    "conversao": row["conversao"]
                }
                logger.info(f"Inserindo registro em bg_fisico para id_produto: {id_produto}")
                supabase.from_('bg_fisico').insert(bg_fisico_data).execute()
            else:
                logger.info(f"Produto {nome_produto} não existe. Inserindo novo produto.")

                # Inserir novo produto na tabela produtos_fisicos
                novo_produto = {
                    "id_plataforma": 2,
                    "nome_produto": nome_produto,
                    "url_produto": row["url_produto"],
                    "url_final": url_final,
                    "preco_comissao": row["preco_comissao"],
                    "desc_produto": row["desc_produto"]
                }
                response = supabase.from_('produtos_fisicos').insert(novo_produto).execute()
                id_produto = response.data[0]['id_produto']

                # Inserir dados na tabela bg_fisico
                bg_fisico_data = {
                    "id_produto": id_produto,
                    "data": row["data"].strftime('%Y-%m-%d'),
                    "localidades": row["localidades"],
                    "restricoes": row["restricoes"],
                    "conversao": row["conversao"]
                }
                logger.info(f"Inserindo registro em bg_fisico para novo produto com id_produto: {id_produto}")
                supabase.from_('bg_fisico').insert(bg_fisico_data).execute()

    except Exception as e:
        logger.error(f'Erro ao processar o arquivo JSON: {e}')

# Caminho absoluto para o arquivo JSON
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, '..', '..', 'extracao', 'semanal', 'resultado_scrape', 'bg_scrape.json')

# Verifica se o arquivo existe antes de tentar processá-lo
if not os.path.isfile(file_path):
    logger.error(f'O arquivo {file_path} não existe.')
else:
    # Chamar a função com o caminho para o arquivo JSON
    upsert_data(file_path)
