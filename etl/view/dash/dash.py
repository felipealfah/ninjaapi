import os
import logging
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client

# Configurar o logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Carregar variáveis de ambiente
load_dotenv()
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_API_KEY = os.getenv('SUPABASE_API_KEY')

# Criar conexão com o Supabase
def connect_supabase():
    return create_client(SUPABASE_URL, SUPABASE_API_KEY)

# Função para consultar a view no Supabase e retornar um DataFrame
def fetch_data_from_view(view_name):
    client = connect_supabase()
    response = client.from_(view_name).select('*').execute()
    if response.data:
        logging.info(f"Dados da view '{view_name}' obtidos com sucesso.")
        return pd.DataFrame(response.data)  # Retorna os dados como DataFrame
    else:
        logging.error(f"Erro ao buscar dados da view {view_name}: {response}")
        return pd.DataFrame()  # Retorna um DataFrame vazio se houver erro

# Função para buscar dados e criar o DataFrame `df_bruto` com colunas específicas
def get_df_bruto():
    view_name = "produtos_ninjaclick_analise"
    df = fetch_data_from_view(view_name)
    if not df.empty:
        df_bruto = df[
            [
                'nome_plataforma', 'nome_real', 'nome_produto', 'ff',
                'mes_atual', 'mes_anterior', 'dois_meses', 'url_final',
                'pais1', 'sharep1', 'pais2', 'sharep2', 'pais3', 'sharep3',
                'pais4', 'sharep4', 'pais5', 'sharep5'
            ]
        ].rename(columns={
            'nome_plataforma': 'Plataforma',
            'nome_real': 'Nome do produto',
            'nome_produto': 'Nome do produto na Plataforma',
            'ff': 'Fundo de Funil',
            'mes_atual': 'Trafego do mês',
            'mes_anterior': 'Trafego mês anterior',
            'dois_meses': 'Trafego dois meses atrás',
            'url_final': 'Site do Produto',
            'pais1': 'Pais 1',
            'sharep1': '% Trafego P1',
            'pais2': 'Pais 2',
            'sharep2': '% Trafego P2',
            'pais3': 'Pais 3',
            'sharep3': '% Trafego P3',
            'pais4': 'Pais 4',
            'sharep4': '% Trafego P4',
            'pais5': 'Pais 5',
            'sharep5': '% Trafego P5'
        })
        logging.info("DataFrame `df_bruto` criado com sucesso com as colunas especificadas.")
        return df_bruto
    else:
        logging.error("A view retornou um DataFrame vazio. Verifique a view ou a conexão com o Supabase.")
        return pd.DataFrame()

# Função para criar o DataFrame `df_transf` com manipulações
def transform_data(df_bruto):
    df_transf = df_bruto.copy()  # Copiar o DataFrame para realizar as manipulações

    # Colunas de tráfego para converter em porcentagem
    trafego_cols = ['% Trafego P1', '% Trafego P2', '% Trafego P3', '% Trafego P4', '% Trafego P5']

    # Substituir valores NaN por 0 para evitar erros de conversão
    df_transf[trafego_cols] = df_transf[trafego_cols].fillna(0)

    # Converter as colunas de tráfego para porcentagem, arredondar e formatar como string
    for col in trafego_cols:
        df_transf[col] = (df_transf[col] * 100).round(0).astype(int).astype(str) + '%'

    # Remover o índice antigo e definir um novo índice sequencial
    df_transf.reset_index(drop=True, inplace=True)

    logging.info("DataFrame `df_transf` criado com as manipulações especificadas.")
    return df_transf

# Função para aplicar filtros ao DataFrame `df_transf`
def filter_data(df, plataforma=None, pais=None):
    # Filtrar por plataforma, se especificado
    if plataforma:
        df = df[df['Plataforma'] == plataforma]
    # Filtrar por país, se especificado
    if pais:
        df = df[(df['Pais 1'] == pais) | (df['Pais 2'] == pais) | 
                (df['Pais 3'] == pais) | (df['Pais 4'] == pais) | 
                (df['Pais 5'] == pais)]
    return df

# Fluxo principal para exibir o DataFrame `df_transf`
if __name__ == "__main__":
    df_bruto = get_df_bruto()
    if not df_bruto.empty:
        logging.info("Exibindo o DataFrame `df_bruto`:")
        logging.info(df_bruto.head())  # Exibe as primeiras linhas para visualização

        # Realizar transformações e exibir `df_transf`
        df_transf = transform_data(df_bruto)
        logging.info("Exibindo o DataFrame `df_transf` com as manipulações:")
        logging.info(df_transf.head())  # Exibe as primeiras linhas de `df_transf`
    else:
        logging.error("O DataFrame `df_bruto` está vazio.")
