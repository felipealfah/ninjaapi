## Extrair e Verifica o nome verdadeiro do produto

import os
import json
import logging
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client
import spacy
import re

# Configurar o logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Carregar variáveis de ambiente
load_dotenv()
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_API_KEY = os.getenv('SUPABASE_API_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_API_KEY)

# Carregar modelo de linguagem do spaCy
nlp = spacy.load("en_core_web_sm")

# Função para buscar produtos do banco de dados
def buscar_produtos():
    try:
        response = supabase.table('produtos_fisicos')\
            .select('id_produto, desc_produto')\
            .eq('id_plataforma', 1)\
            .execute()
        produtos = response.data
        return produtos
    except Exception as e:
        logging.error(f"Erro ao buscar produtos: {e}")
        return []

# Função para extrair o nome do produto da descrição
def extrair_nome_produto(descricao):
    descricao = re.sub(r'[^\w\s-]', '', descricao)  # Remove caracteres especiais
    descricao = descricao.strip()  # Remover espaços em branco nas extremidades
    doc = nlp(descricao)

    for ent in doc.ents:
        if ent.label_ == 'PRODUCT':
            return ent.text.strip()

    if ':' in descricao:
        return descricao.split(':')[0].strip()

    palavras_chave = ['EPC', 'VSL', 'NEW', 'Offer', 'for', 'is', 'avg', '$']
    for palavra in palavras_chave:
        if palavra in descricao:
            nome_produto = descricao.split(palavra)[0].strip()
            nome_produto = re.sub(r'\d+', '', nome_produto).strip()  # Remove números
            return ' '.join(nome_produto.split()).strip()  # Limpa espaços

    partes = descricao.split('-')
    if partes:
        nome_produto = partes[0].strip()
        return ' '.join(nome_produto.split()).strip()  # Limpar espaços

    return "Nome não encontrado"

# Função para verificar se o produto já existe na tabela
def produto_existe(id_produto):
    try:
        response = supabase.table('kw_volume')\
            .select('id_produto')\
            .eq('id_produto', id_produto)\
            .execute()
        return len(response.data) > 0
    except Exception as e:
        logging.error(f"Erro ao verificar produto: {e}")
        return False

# Função para inserir novo produto
def inserir_produto(id_produto, nome_produto):
    try:
        response = supabase.table('kw_volume').insert({
            'id_produto': id_produto,
            'nome_produto': nome_produto
        }).execute()
        logging.info(f"Produto inserido: {id_produto} - {nome_produto}")
    except Exception as e:
        logging.error(f"Erro ao inserir produto: {e}")

# Função principal
def main():
    produtos = buscar_produtos()
    
    if produtos:
        df_produtos = pd.DataFrame(produtos)
        df_produtos['nome_extraido'] = df_produtos['desc_produto'].apply(extrair_nome_produto)

        for index, row in df_produtos.iterrows():
            id_produto = row['id_produto']
            nome_produto = row['nome_extraido']
            
            if not produto_existe(id_produto):
                inserir_produto(id_produto, nome_produto)
            else:
                logging.info(f"Produto já existe: {id_produto} - não será inserido.")

if __name__ == "__main__":
    main()
