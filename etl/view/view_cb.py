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
    view_name = 'view_produtos_clickbank_api'
    
    # Consultar a view e construir o DataFrame
    data = fetch_data_from_view(view_name)
    
    if data:
        df = pd.DataFrame(data)
        
        # Normalizar os nomes das colunas para evitar duplicações
        df.columns = [col.lower() for col in df.columns]

        # Renomear as colunas
        df.rename(columns={
            'first_see': 'primeira aparição',
            'mes_atual': 'trafego_mes_atual',
            'mes_anterior': 'trafego_mes_anterior',
            'dois_meses': 'trafego_dois_meses_atras'
        }, inplace=True)

        # Converter a coluna 'data' para datetime se necessário
        if 'data' in df.columns:
            df['data'] = pd.to_datetime(df['data'])
            ultima_atualizacao = df['data'].max().strftime('%Y-%m-%d %H:%M:%S')
            df['data'] = df['data'].dt.strftime('%Y-%m-%d %H:%M:%S')  # Converter a coluna 'data' para string
        else:
            ultima_atualizacao = None
        
        # Identificar todas as colunas esperadas pela view
        expected_columns = [
            'id_produto', 'nome_produto', 'desc_produto', 'preco_comissao', 'url_afiliado', 
            'trafego_mes_atual', 'trafego_mes_anterior', 'trafego_dois_meses_atras', 'pais1', 'pais2', 'pais3', 
            'pais4', 'pais5', 'valor_gravity', 'ranking', 'data',
            'gravity_dia', 'gravity_7d', 'gravity_15d', 'gravity_30d', 
            'gravity_45d', 'gravity_60d', 'gravity_90d', 'primeira aparição'
        ]
        
        # Garantir que todas as colunas esperadas estejam presentes no DataFrame
        for col in expected_columns:
            if col not in df.columns:
                df[col] = None  # Adiciona a coluna com valores None se não existir

        # Reordenar as colunas conforme a lista expected_columns
        df = df[expected_columns]

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
