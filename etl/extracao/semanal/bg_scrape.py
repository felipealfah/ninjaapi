import json
import os
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuração do logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configurar o WebDriver remoto
options = webdriver.ChromeOptions()
driver = webdriver.Remote(
    command_executor='http://api.fulled.com.br:4444/wd/hub',
    options=options
)

# Lista para armazenar os resultados
results = []

try:
    logger.info('Acessando a página inicial.')
    driver.get('https://backoffice.buygoods.com/campaigns#0')

    # Aguarde o carregamento dos produtos
    wait = WebDriverWait(driver, 20)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.product-line')))
    logger.info('Página inicial carregada com sucesso.')

    # Função para verificar e extrair texto de um elemento
    def get_element_text_or_default(element, selector, default_value):
        try:
            return element.find_element(By.CSS_SELECTOR, selector).text
        except:
            return default_value

    # Função para verificar e extrair texto de um elemento usando XPath
    def get_element_text_or_default_xpath(element, xpath, default_value):
        try:
            return element.find_element(By.XPATH, xpath).text.split(":", 1)[1].strip()
        except:
            return default_value

    # Função para extrair dados dos produtos
    def extract_products(page_number):
        logger.info(f'Extraindo produtos da página {page_number}.')
        products = driver.find_elements(By.CSS_SELECTOR, 'div.product-line')
        for product in products:
            try:
                # Nome do produto e link do produto
                product_name_element = product.find_element(By.CSS_SELECTOR, 'h1 > a > label#cartproductname')
                title = product_name_element.text
                product_link = product.find_element(By.CSS_SELECTOR, 'h1 > a').get_attribute('href')

                # Descrição do produto
                description = get_element_text_or_default(product, 'div.col-md-6 > div > p', 'Descrição não disponível')

                # Taxa de conversão
                conversion_rate = get_element_text_or_default(product, 'div.col.text-center.align-self-center.col-3 > span', '0%')

                # Allowed Geos e Restrictions
                allowed_geos = get_element_text_or_default_xpath(product, ".//div[@class='mentions']//p[span[strong[contains(text(),'Allowed Geos:')]]]", 'Não disponível')
                restrictions = get_element_text_or_default_xpath(product, ".//div[@class='mentions']//p[span[strong[contains(text(),'Restrictions:')]]]", 'Não disponível')

                # Average Payout
                average_payout = get_element_text_or_default(product, 'div.mb-2 > span.offer-explained > strong > span', '0.00')

                # Adicionar os dados do produto à lista de resultados
                results.append({
                    'title': title,
                    'description': description,
                    'conversion_rate': conversion_rate,
                    'product_link': product_link,
                    'allowed_geos': allowed_geos,
                    'restrictions': restrictions,
                    'average_payout': average_payout
                })

            except Exception as e:
                logger.error(f'Erro ao extrair informações do produto: {e}')

    # Extraia produtos da primeira página
    extract_products(page_number=1)

    # Navegue pelas páginas
    page_number = 1
    while True:
        try:
            # Verifique se o botão "Next" está presente
            next_button = driver.find_elements(By.CSS_SELECTOR, 'li.next > a')
            
            if not next_button:
                logger.info('Não há mais páginas para navegar. Fim da extração.')
                break
            
            next_button = next_button[0]

            # Aguarde o botão "Next" estar visível e clicável
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'li.next > a')))

            # Use JavaScript para clicar no botão "Next"
            driver.execute_script("arguments[0].click();", next_button)
            page_number += 1

            # Aguarde os novos produtos carregarem
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.product-line')))

            # Extraia produtos da nova página
            extract_products(page_number)
        except Exception as e:
            logger.error(f'Erro ao navegar pela página: {e}')
            break

finally:
    # Encerre o driver
    driver.quit()
    logger.info('Driver encerrado.')

    # Certifique-se de que a pasta 'resultado_scrape' exista
    os.makedirs('resultado_scrape', exist_ok=True)

    # Adicionar a data de criação ao JSON
    data_criacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Dicionário final para o JSON
    final_result = {
        'data_criacao': data_criacao,
        'produtos': results
    }

    # Caminho do arquivo JSON
    output_file = os.path.join('resultado_scrape', 'bg_scrape.json')

    # Salvar os resultados em um arquivo JSON (substitui se já existir)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_result, f, ensure_ascii=False, indent=4)

    logger.info(f'Resultados salvos em {output_file}')
    logger.info(f'Total de produtos extraídos: {len(results)}')
