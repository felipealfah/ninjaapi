import os
import json
import logging
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

# Função para atualizar a coluna url_final na tabela produtos_fisicos
def update_supabase(data):
    for produto in data:
        nome_produto = produto['nome_produto']
        url_final = produto['url_final']

        # Atualizar a coluna url_final na tabela produtos_fisicos
        update_data = {"url_final": url_final}
        response = supabase.from_('produtos_fisicos').update(update_data).eq('nome_produto', nome_produto).execute()

        if response.data:
            logging.info(f"Produto {nome_produto} atualizado com sucesso.")
        elif response.error:
            logging.error(f"Erro ao atualizar {nome_produto}: {response.error}")
        else:
            logging.error(f"Erro desconhecido ao atualizar {nome_produto}: {response}")

# Função principal
def main():
    input_file = os.path.join(os.path.dirname(__file__), 'resultado_trans', 'url_final.json')
    
    # Ler o arquivo JSON
    data = read_json_file(input_file)
    
    # Atualizar Supabase
    update_supabase(data)
    
    logging.info("Atualização concluída.")

if __name__ == "__main__":
    main()
