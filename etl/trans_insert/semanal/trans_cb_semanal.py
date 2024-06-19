import os
import json
from dotenv import load_dotenv
from supabase import create_client, Client
from urllib.parse import urlparse

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
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception as e:
        print(f"Erro ao extrair domínio de {url}: {e}")
        return None

# Função para atualizar o banco de dados
def update_product_urls(data):
    for produto in data:
        nome_produto = produto['nome_produto']
        url_produto = produto['url_produto']
        url_afiliado = produto['url_afiliado']
        url_final = extract_domain(url_afiliado)

        # Buscar o produto no banco de dados pelo nome
        response = supabase.from_('produtos_fisicos').select('id_produto').eq('nome_produto', nome_produto).execute()
        if response.data:
            id_produto = response.data[0]['id_produto']
            print(f"Atualizando produto {nome_produto} com id {id_produto}")

            # Atualizar as colunas url_produto, url_afiliado e url_final
            update_data = {
                "url_produto": url_produto,
                "url_afiliado": url_afiliado,
                "url_final": url_final  # Adicionando a nova coluna
            }
            supabase.from_('produtos_fisicos').update(update_data).eq('id_produto', id_produto).execute()
        else:
            print(f"Produto {nome_produto} não encontrado no banco de dados.")

# Função principal
def main():
    #file_path = '../../extracao/semanal/resultado_scrape/cb_scrape_semanal.json'
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
