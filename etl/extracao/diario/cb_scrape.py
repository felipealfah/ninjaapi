import os
import json
import requests
import datetime
import logging
from bs4 import BeautifulSoup

# Configurando o logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

def fazer_scrape(url_template):
    pagina = 1
    produtos = []
    data_de_criacao = datetime.datetime.now().strftime("%Y-%m-%d")
    
    while True:
        # Construindo a URL da página atual
        url = url_template.format(pagina=pagina)
        
        # Log para indicar a página sendo processada
        logging.info(f"Processando página {pagina}...")
        
        # Fazendo uma solicitação HTTP GET para obter o conteúdo da página
        response = requests.get(url)
        
        # Verificando se a solicitação foi bem-sucedida (código de status 200)
        if response.status_code == 200:
            # Log de sucesso ao obter a página
            logging.info(f"Extração da página {pagina} bem-sucedida.")
            
            # Criando um objeto BeautifulSoup com o conteúdo HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Verificando se a mensagem "No items found" está presente na página
            no_items_message = soup.find("span", class_="font-medium py-8 text-gray-400 text-lg dark:text-white")
            if no_items_message:
                # Log de aviso e encerramento da extração se a mensagem for encontrada
                logging.warning("Mensagem 'No items found. Try to broaden your search.' encontrada. Encerrando a extração.")
                break
            
            # Encontrando a tabela
            tabela = soup.find('table', class_='min-w-full')
            
            # Verificando se a tabela foi encontrada
            if tabela:
                # Iterando sobre as linhas da tabela
                for linha in tabela.find_all('tr'):
                    # Iterando sobre as células da linha
                    celulas = linha.find_all('td')
                    if celulas:
                        # Verificando se há células suficientes
                        if len(celulas) >= 7:
                            # Extraindo os dados das células
                            ranking = celulas[0].get_text().strip()
                            product = celulas[1].get_text().strip()
                            title = celulas[2].get_text().strip()
                            gravity = celulas[3].get_text().strip()
                            av_sale = celulas[5].get_text().strip()
                            rebill = celulas[6].get_text().strip()
                            
                            # Adicionando os dados do produto à lista de produtos
                            produtos.append({
                                "Ranking": ranking,
                                "Product": product,
                                "Title": title,
                                "Gravity": gravity,
                                "Av_/Sale": av_sale,
                                "Rebill": rebill,
                                "Data_Criacao": data_de_criacao  # Adicionando a data de criação
                            })

                # Indo para a próxima página
                pagina += 1
            else:
                # Se a tabela não for encontrada, a página está vazia
                # Terminando a extração
                logging.warning("Tabela não encontrada na página. Terminando a extração.")
                break
        else:
            # Log de erro ao fazer a solicitação HTTP
            logging.error(f"Falha ao carregar a página {pagina}: {response.status_code}")
            break
    
    # Verificando se há produtos extraídos
    if produtos:
        # Diretório para salvar o arquivo JSON
        resultado_scrape_dir = os.path.join(os.path.dirname(__file__), 'resultado_scrape')

        # Verificando se o diretório 'resultado_scrape' existe
        if not os.path.exists(resultado_scrape_dir):
            os.makedirs(resultado_scrape_dir)
        
        # Definindo o caminho completo para o arquivo JSON
        arquivo_json = os.path.join(resultado_scrape_dir, 'cb_scrape.json')
        
        # Escrevendo os resultados em um arquivo JSON
        with open(arquivo_json, "w") as json_file:
            json.dump({"data_criacao": data_de_criacao, "Produtos": produtos}, json_file, indent=4)
            logging.info(f"Arquivo JSON salvo em {arquivo_json}")
    else:
        # Log de aviso se nenhum produto foi extraído
        logging.warning("Nenhum produto extraído.")

def main():
    # URL da página para scraping
    url_template = "https://cbsnooper.com/reports/top-clickbank-products?table[filters][physical_products]=1&page={pagina}"
    
    # Realizando o scraping
    fazer_scrape(url_template)

if __name__ == "__main__":
    main()
