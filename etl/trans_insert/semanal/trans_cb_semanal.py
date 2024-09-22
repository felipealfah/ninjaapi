import os
import json
from dotenv import load_dotenv
from supabase import create_client, Client
from urllib.parse import urlparse
from datetime import datetime

# Carregar variáveis de ambiente
load_dotenv()
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_API_KEY = os.getenv('SUPABASE_API_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_API_KEY)

# Função para ler o arquivo JSON
def read_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Função para extrair o domínio da URL e remover "www"
def extract_domain(url):
    if not url:
        print(f"URL é None ou vazia. Não é possível extrair domínio.")
        return None
    
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception as e:
        print(f"Erro ao extrair domínio de {url}: {e}")
        return None

# Função para converter data para o formato YYYY-MM-DD
def convert_to_date(date_string):
    if not date_string:
        print(f"Data é None ou vazia. Não é possível converter.")
        return None
    
    try:
        # Converte a string "Thu, Jul 20, 2023" para um objeto datetime
        date_obj = datetime.strptime(date_string, '%a, %b %d, %Y')
        # Retorna a data no formato YYYY-MM-DD
        return date_obj.strftime('%Y-%m-%d')
    except Exception as e:
        print(f"Erro ao converter data {date_string}: {e}")
        return None

# Função para atualizar o banco de dados
def update_product_urls(data):
    for produto in data:
        nome_produto = produto.get('nome_produto')
        url_produto = produto.get('url_produto')
        url_afiliado = produto.get('url_afiliado')
        first_seen_date = convert_to_date(produto.get('first_seen_date'))  # Convertendo a data
        url_final = extract_domain(url_afiliado)

        if nome_produto is None:
            print("Nome do produto é None. Não é possível atualizar.")
            continue

        # Buscar o produto no banco de dados pelo nome
        response = supabase.from_('produtos_fisicos').select('id_produto').eq('nome_produto', nome_produto).execute()

        # Verificar se a resposta contém dados
        if response.data:
            id_produto = response.data[0]['id_produto']
            print(f"Atualizando produto {nome_produto} com id {id_produto}")

            # Atualizar as colunas url_produto, url_afiliado, url_final e first_seen_date
            update_data = {
                "url_produto": url_produto,
                "url_afiliado": url_afiliado,
                "url_final": url_final,  # Adicionando a nova coluna
                "first_see": first_seen_date  # Adicionando a coluna first_see
            }
            supabase.from_('produtos_fisicos').update(update_data).eq('id_produto', id_produto).execute()
        else:
            print(f"Produto {nome_produto} não encontrado no banco de dados.")

# Função principal
def main():
    # Caminho absoluto para o arquivo JSON
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, '..', '..', 'extracao', 'semanal', 'resultado_scrape', 'cb_scrape_semanal.json')

    # Ler o arquivo JSON
    data = read_json_file(file_path)

    # Atualizar o banco de dados
    update_product_urls(data)

    print("Atualização concluída.")

# Executar a função principal
if __name__ == "__main__":
    main()
