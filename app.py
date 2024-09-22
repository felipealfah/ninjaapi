from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import os
import json
import logging

# Importando o módulo njapi que contém a função get_screenshots
from api_ninjapresell import njapi


# Configurando o logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

json_file_path = '/ninja/etl/view/resultado/clickbank_resultado.json'

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

@app.post("/bgninjapresell")
async def get_presell_data(request: Request):
    try:
        body = await request.json()
        url = body.get('url')
        if not url:
            raise HTTPException(status_code=400, detail="URL não fornecida")
        
        response_content = njapi.get_screenshots(url)
        return JSONResponse(content=response_content)
    except ValueError as e:
        logging.error(f"Erro no processamento da URL: {str(e)}")
        raise HTTPException(status_code=422, detail=f"Erro no processamento da URL: {str(e)}")
    except Exception as e:
        logging.error(f"Erro ao processar screenshot: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar screenshot: {str(e)}")

