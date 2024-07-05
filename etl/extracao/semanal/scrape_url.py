import os
import json
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client
import logging

# Configurar o logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Carregar variáveis de ambiente
load_dotenv()
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_API_KEY = os.getenv('SUPABASE_API_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_API_KEY)

# Função para buscar produtos onde url_final é null
def fetch_products_without_url():
    response = supabase.from_('produtos_fisicos').select('nome_produto').is_('url_final', None).execute()
    if response.data:
        return response.data
    else:
        logging.error(f"Erro ao buscar produtos: {response}")
        return []

# Função principal
def main():
    # Buscar produtos
    produtos = fetch_products_without_url()
    
    # Criar DataFrame
    if produtos:
        df = pd.DataFrame(produtos)
        df['url_visitada'] = df['nome_produto'].apply(lambda x: f'https://cbsnooper.com/visit/{x}')
        
        # Converter DataFrame para dicionário
        result = df.to_dict(orient='records')

        # Gerar JSON e salvar
        output_dir = os.path.join(os.path.dirname(__file__), 'resultado_scrape')
        output_file = os.path.join(output_dir, 'scrape_url.json')
        
        os.makedirs(output_dir, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=4)
        
        logging.info(f"Arquivo JSON salvo com sucesso em {output_file}")
    else:
        logging.info("Nenhum produto encontrado para processar.")

if __name__ == "__main__":
    main()
