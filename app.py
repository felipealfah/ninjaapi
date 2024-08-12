from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import os
import json

# Crie uma instância do FastAPI
app = FastAPI()

# Defina o caminho para o arquivo JSON
json_file_path = os.path.join(os.path.dirname(__file__), 'view', 'resultado', 'clickbank_resultado.json')

# Rota para obter os dados do JSON
@app.get("/clickbank")
async def get_clickbank_data():
    try:
        # Verifique se o arquivo JSON existe
        if not os.path.exists(json_file_path):
            raise HTTPException(status_code=404, detail="Arquivo JSON não encontrado")
        
        # Leia o conteúdo do arquivo JSON
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)
        
        # Retorne os dados como resposta JSON
        return JSONResponse(content=data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Rota para verificar se a API está funcionando
@app.get("/")
async def root():
    return {"message": "API para Clickbank está funcionando!"}

# Comando para rodar o servidor Uvicorn se este script for executado diretamente
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
