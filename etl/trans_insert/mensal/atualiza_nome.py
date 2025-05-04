import os
import logging
from dotenv import load_dotenv
from supabase import create_client, Client
import re

# Configurar o logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Carregar variáveis de ambiente
load_dotenv()
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_API_KEY = os.getenv('SUPABASE_API_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_API_KEY)

# Função para atualizar a coluna "nome_produto"
def atualizar_nome_produto():
    try:
        # Buscar todos os produtos da tabela "kw_volume"
        response = supabase.table('kw_volume').select('id, nome_produto').execute()
        produtos = response.data

        if produtos:
            for produto in produtos:
                id_produto = produto['id']
                nome_produto = produto['nome_produto']

                # Remover texto após "-" e limpar espaços
                novo_nome_produto = re.sub(r'\s*-\s*.*$', '', nome_produto).strip()

                # Atualizar a tabela apenas se o nome mudou
                if novo_nome_produto != nome_produto:
                    supabase.table('kw_volume').update({'nome_produto': novo_nome_produto}).eq('id', id_produto).execute()
                    logging.info(f"Atualizado: id {id_produto} - nome_produto de '{nome_produto}' para '{novo_nome_produto}'")
                else:
                    logging.info(f"Nenhuma atualização necessária para id {id_produto}: '{nome_produto}'")

    except Exception as e:
        logging.error(f"Erro ao atualizar nome_produto: {e}")

# Função principal
def main():
    atualizar_nome_produto()

if __name__ == "__main__":
    main()
