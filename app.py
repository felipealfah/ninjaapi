from fastapi import FastAPI, HTTPException, Response
import os

app = FastAPI()


@app.get("/", response_model=str)
async def index():
    return "<h1>Welcome to the Scrape Ninja App</h1>"

@app.get("/results")
async def get_scrape_results():
    try:
        with open("scrape/resultado_scrape.json", 'r') as f:
            return Response(content=f.read(), media_type="application/json")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Resultado JSON não encontrado.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8080)
