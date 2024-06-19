import os
import json
import logging
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client

# Configurar o logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Carregar variáveis de ambiente
load_dotenv()
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_API_KEY = os.getenv('SUPABASE_API_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_API_KEY)

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

# Função para buscar id_produto pelo nome do produto
def fetch_product_id_by_name(nome_produto):
    try:
        response = supabase.from_('produtos_fisicos').select('id_produto').eq('nome_produto', nome_produto).execute()
        if response.data:
            return response.data[0]['id_produto']
        else:
            logging.error(f"Produto com nome {nome_produto} não encontrado.")
            return None
    except Exception as e:
        logging.error(f"Erro ao buscar id_produto para {nome_produto}: {e}")
        return None

# Função para verificar se o id_produto existe na tabela mensal_fisico
def check_if_product_exists(id_produto):
    try:
        response = supabase.from_('mensal_fisico').select('id_produto').eq('id_produto', id_produto).execute()
        return bool(response.data)
    except Exception as e:
        logging.error(f"Erro ao verificar existência do produto com id {id_produto}: {e}")
        return False

# Função para tratar valores NaN
def sanitize_value(value, default=0):
    return default if pd.isna(value) else int(value)

# Função para inserir ou atualizar a tabela mensal_fisico no Supabase
def upsert_supabase(df):
    for index, row in df.iterrows():
        try:
            id_produto = fetch_product_id_by_name(row['nome_produto'])
            if id_produto:
                update_data = {
                    "id_produto": id_produto,
                    "mes_atual": sanitize_value(row['mes_atual']),
                    "mes_anterior": sanitize_value(row['mes_anterior']),
                    "dois_meses": sanitize_value(row['dois_meses']),
                    "pais1": row['pais1'],
                    "pais2": row['pais2'],
                    "pais3": row['pais3'],
                    "pais4": row['pais4'],
                    "pais5": row['pais5']
                }
                if check_if_product_exists(id_produto):
                    logging.info(f"Atualizando id_produto {id_produto} com dados: {update_data}")
                    response = supabase.from_('mensal_fisico').update(update_data).eq('id_produto', id_produto).execute()
                else:
                    logging.info(f"Inserindo novo produto com id_produto {id_produto} com dados: {update_data}")
                    response = supabase.from_('mensal_fisico').insert(update_data).execute()
                    
                logging.info(f"Resposta completa da API para id_produto {id_produto}: {response}")
                
                if response.data:
                    logging.info(f"Produto com id {id_produto} atualizado/inserido com sucesso.")
                else:
                    logging.error(f"Erro ao atualizar/inserir produto com id {id_produto}: {response}")
            else:
                logging.error(f"Não foi possível encontrar id_produto para {row['nome_produto']}")
        except ValueError as e:
            logging.error(f"Erro de valor ao processar o produto com nome {row['nome_produto']}: {e}")
        except Exception as e:
            logging.error(f"Erro ao atualizar/inserir produto com nome {row['nome_produto']}: {e}")

# Função principal
def main():
    input_file = os.path.join(os.path.dirname(__file__), 'resultado_quinze', 'trans_trafego.json')
    
    # Ler o arquivo JSON
    data = read_json_file(input_file)
    
    # Criar DataFrame
    df = pd.DataFrame(data)
    
    # Atualizar ou inserir no Supabase
    upsert_supabase(df)
    
    logging.info("Atualização/inserção concluída.")

if __name__ == "__main__":
    main()
