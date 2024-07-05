from dotenv import load_dotenv
import os
import json
import pandas as pd
from supabase import create_client, Client

# Carregar variáveis de ambiente
load_dotenv()
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_API_KEY = os.getenv('SUPABASE_API_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_API_KEY)

# Função para ler o arquivo JSON
def read_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Função para transformar os dados em um DataFrame
def transform_data(data):
    produtos = data["Produtos"]

    # Criar DataFrame
    df = pd.DataFrame(produtos)

    # Renomear colunas conforme necessário
    df = df.rename(columns={
        "Ranking": "ranking",
        "Product": "nome_produto",
        "Title": "desc_produto",
        "Gravity": "valor_gravity",
        "Av_/Sale": "preco_comissao",
        "Rebill": "preco_rebill",
        "Data_Criacao": "data"
    })

    # Adicionar coluna url_produto como string vazia
    df["url_produto"] = ""

    # Converter tipos de dados e ajustar formatação
    df["preco_comissao"] = df["preco_comissao"].str.replace("$", "").astype(float)
    df["preco_rebill"] = df["preco_rebill"].str.replace("$", "").astype(float)
    df["valor_gravity"] = df["valor_gravity"].str.replace('.', '').astype(int)
    df["ranking"] = df["ranking"].astype(int)
    df["data"] = pd.to_datetime(df["data"])

    # Verificação dos valores convertidos
    print("Valores de preco_comissao:", df["preco_comissao"].head())
    print("Valores de preco_rebill:", df["preco_rebill"].head())

    return df

# Função para verificar se o produto existe e inserir/atualizar dados
def upsert_data(file_path):
    try:
        data = read_json_file(file_path)
        df = transform_data(data)

        for index, row in df.iterrows():
            nome_produto = row["nome_produto"]

            # Verificar se o produto já existe na tabela produtos_fisicos
            response = supabase.from_('produtos_fisicos').select('id_produto').eq('nome_produto', nome_produto).execute()
            if response.data:
                id_produto = response.data[0]['id_produto']
                print(f"Produto {nome_produto} já existe com id {id_produto}. Atualizando cb_diario_fisico.")

                # Verificar se o registro já existe na tabela cb_diario_fisico
                cb_response = supabase.from_('cb_diario_fisico').select('id_diario').eq('id_produto', id_produto).eq('data', row["data"].strftime('%Y-%m-%d')).execute()
                if cb_response.data:
                    # Atualizar registro existente em cb_diario_fisico
                    cb_diario_data = {
                        "valor_gravity": row["valor_gravity"],
                        "ranking": row["ranking"]
                    }
                    print(f"Atualizando cb_diario_fisico com id_diario: {cb_response.data[0]['id_diario']}")
                    supabase.from_('cb_diario_fisico').update(cb_diario_data).eq('id_diario', cb_response.data[0]['id_diario']).execute()
                else:
                    # Inserir novo registro em cb_diario_fisico, sem especificar id_diario
                    cb_diario_data = {
                        "id_produto": id_produto,
                        "data": row["data"].strftime('%Y-%m-%d'),
                        "valor_gravity": row["valor_gravity"],
                        "ranking": row["ranking"]
                    }
                    print(f"Inserindo novo registro em cb_diario_fisico para id_produto: {id_produto}")
                    supabase.from_('cb_diario_fisico').insert(cb_diario_data).execute()
            else:
                print(f"Produto {nome_produto} não existe. Inserindo novo produto.")

                # Inserir novo produto na tabela produtos_fisicos
                novo_produto = {
                    "id_plataforma": 1,
                    "nome_produto": nome_produto,
                    "url_produto": row["url_produto"],
                    "url_afiliado": "",
                    "preco_comissao": row["preco_comissao"],
                    "preco_rebill": row["preco_rebill"],
                    "desc_produto": row["desc_produto"]
                }
                response = supabase.from_('produtos_fisicos').insert(novo_produto).execute()
                id_produto = response.data[0]['id_produto']

                # Inserir dados na tabela cb_diario_fisico, sem especificar id_diario
                cb_diario_data = {
                    "id_produto": id_produto,
                    "data": row["data"].strftime('%Y-%m-%d'),
                    "valor_gravity": row["valor_gravity"],
                    "ranking": row["ranking"]
                }
                print(f"Inserindo novo registro em cb_diario_fisico para novo produto com id_produto: {id_produto}")
                supabase.from_('cb_diario_fisico').insert(cb_diario_data).execute()

    except Exception as e:
        print('Erro ao processar o arquivo JSON:', e)

# Caminho absoluto para o arquivo JSON
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, '..', '..', 'extracao', 'diario', 'resultado_scrape', 'cb_scrape.json')

# Chamar a função com o caminho para o arquivo JSON
upsert_data(file_path)
