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
SUPABASE_API_KEY = os.getenv('SUPABASE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_API_KEY)

# Função para consultar a view no Supabase
def fetch_data_from_view(view_name):
    response = supabase.from_(view_name).select('*').execute()
    if response.data:
        return response.data
    else:
        logging.error(f"Erro ao buscar dados da view {view_name}: {response}")
        return []

# Função principal
def main():
    # Nome da view que você quer consultar
    view_name = 'view_produtos_clickbank_ff'
    
    # Consultar a view e construir o DataFrame
    data = fetch_data_from_view(view_name)
    
    if data:
        df = pd.DataFrame(data)
        
        # Converter a coluna 'data' para datetime se necessário
        if 'data' in df.columns:
            df['data'] = pd.to_datetime(df['data'])
            ultima_atualizacao = df['data'].max().strftime('%Y-%m-%d %H:%M:%S')
            df['data'] = df['data'].dt.strftime('%Y-%m-%d %H:%M:%S')  # Converter a coluna 'data' para string
        else:
            ultima_atualizacao = None
        
        # Diretório para salvar o arquivo JSON
        resultado_scrape_dir = os.path.join(os.path.dirname(__file__), 'resultado')

        # Verificando se o diretório 'resultado' existe
        if not os.path.exists(resultado_scrape_dir):
            os.makedirs(resultado_scrape_dir)
        
        # Definindo o caminho completo para o arquivo JSON
        arquivo_json = os.path.join(resultado_scrape_dir, 'clickbank_resultado.json')
        
        # Preparando o dicionário para salvar
        output_data = {
            "ultima_atualizacao": ultima_atualizacao,
            "dados": df.to_dict(orient='records')
        }
        
        # Escrevendo os resultados em um arquivo JSON
        with open(arquivo_json, "w") as json_file:
            json.dump(output_data, json_file, indent=4)
            logging.info(f"Arquivo JSON salvo em {arquivo_json}")
    else:
        # Log de aviso se nenhum dado foi extraído
        logging.warning("Nenhum dado foi retornado da view.")

if __name__ == "__main__":
    main()
