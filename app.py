from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse
import os
import json
import logging
import subprocess

from starlette.responses import RedirectResponse

# Importando o módulo njapi e as funções validar_url e get_screenshots
from api_ninjapresell.njapi import validar_url, get_screenshots
# Importando o script de extração de URLs da subpasta etl_v2
from etl_v2 import url_final_cb

# Configurando o logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

json_file_path = '/ninja/etl/view/resultado/clickbank_resultado.json'
json_file_pathv2 = '/ninja/etl/view/resultado/clickbank_resultadov2.json'

@app.get("/clickbank")
async def get_clickbank_data():
    logging.info(f"Tentando acessar o arquivo JSON em: {json_file_path}")
    try:
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)
            logging.info("Arquivo JSON carregado com sucesso.")
            return JSONResponse(content=data)
    except FileNotFoundError:
        logging.error("Arquivo JSON não encontrado no caminho especificado.")
        raise HTTPException(status_code=404, detail="Arquivo JSON não encontrado")
    except json.JSONDecodeError:
        logging.error("Falha ao decodificar o arquivo JSON.")
        raise HTTPException(status_code=500, detail="Erro na leitura do arquivo JSON")
    
@app.get("/clickbankv2")
async def get_clickbank_data():
    logging.info(f"Tentando acessar o arquivo JSON em: {json_file_pathv2}")
    try:
        with open(json_file_pathv2, 'r') as json_file:
            data = json.load(json_file)
            logging.info("Arquivo JSON carregado com sucesso.")
            return JSONResponse(content=data)
    except FileNotFoundError:
        logging.error("Arquivo JSON não encontrado no caminho especificado.")
        raise HTTPException(status_code=404, detail="Arquivo JSON não encontrado")
    except json.JSONDecodeError:
        logging.error("Falha ao decodificar o arquivo JSON.")
        raise HTTPException(status_code=500, detail="Erro na leitura do arquivo JSON")

@app.post("/bgninjapresell")
async def get_presell_data(request: Request):
    try:
        body = await request.json()
        url = body.get('url')

        if not url:
            raise HTTPException(status_code=400, detail="URL não fornecida")

        if not validar_url(url):
            raise HTTPException(status_code=422, detail="URL inválida")

        # Supondo que `get_screenshots` esteja bem definido e retorne o conteúdo necessário
        response_content = get_screenshots(url)
        return JSONResponse(content=response_content)

    except ValueError as e:
        logging.error(f"Erro no processamento da URL: {str(e)}")
        raise HTTPException(status_code=422, detail=f"Erro no processamento da URL: {str(e)}")
    except json.JSONDecodeError:
        logging.error("Erro ao decodificar JSON da requisição.")
        raise HTTPException(status_code=400, detail="Erro ao decodificar JSON da requisição.")
    except Exception as e:
        logging.error(f"Erro ao processar screenshot: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar screenshot: {str(e)}")


# Função para rodar scripts e capturar saída
def run_script(script_name):
    result = subprocess.run(['python3', script_name], capture_output=True, text=True)
    return result.stdout, result.returncode


# Função para rodar o script diario.py
def run_diario():
    stdout, returncode = run_script('diario.py')
    if returncode != 0:
        logging.error(f"Erro ao executar diario.py: {stdout}")
    else:
        logging.info(f"Script diario.py concluído com sucesso: {stdout}")


# Função para rodar o script semanal.py
def run_semanal():
    stdout, returncode = run_script('semanal.py')
    if returncode != 0:
        logging.error(f"Erro ao executar semanal.py: {stdout}")
    else:
        logging.info(f"Script semanal.py concluído com sucesso: {stdout}")


# Função para rodar o script quinzenal.py
def run_quinzenal():
    stdout, returncode = run_script('quinzenal.py')
    if returncode != 0:
        logging.error(f"Erro ao executar quinzenal.py: {stdout}")
    else:
        logging.info(f"Script quinzenal.py concluído com sucesso: {stdout}")


# Endpoint para rodar o script diario.py em segundo plano
@app.post("/executar-diario")
async def executar_diario(background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(run_diario)
        return {"message": "Script diario.py iniciado em segundo plano"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao iniciar diario.py: {str(e)}")


# Endpoint para rodar o script semanal.py em segundo plano
@app.post("/executar-semanal")
async def executar_semanal(background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(run_semanal)
        return {"message": "Script semanal.py iniciado em segundo plano"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao iniciar semanal.py: {str(e)}")


# Endpoint para rodar o script quinzenal.py em segundo plano
@app.post("/executar-quinzenal")
async def executar_quinzenal(background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(run_quinzenal)
        return {"message": "Script quinzenal.py iniciado em segundo plano"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao iniciar quinzenal.py: {str(e)}")

json_url_final_path = '/ninja/etl_v2/scrape_url_final.json'
@app.get("/processar_urls")
async def get_clickbank_data():
    logging.info(f"Tentando acessar o arquivo JSON em: {json_url_final_path}")
    try:
        with open(json_url_final_path, 'r') as json_file:
            data = json.load(json_file)
            logging.info("Arquivo JSON carregado com sucesso.")
            return JSONResponse(content=data)
    except FileNotFoundError:
        logging.error("Arquivo JSON não encontrado no caminho especificado.")
        raise HTTPException(status_code=404, detail="Arquivo JSON não encontrado")
    except json.JSONDecodeError:
        logging.error("Falha ao decodificar o arquivo JSON.")
        raise HTTPException(status_code=500, detail="Erro na leitura do arquivo JSON")
    
@app.get("/dashboard")
async def redirect_to_dashboard():
    return RedirectResponse(url="http://api.fulled.com.br:8501") 