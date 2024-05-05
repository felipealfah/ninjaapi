# app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
from login.login import async_login_to_cbsnooper_and_transfer_session
from scrape.scrape import parse_all_pages_requests

app = FastAPI()
URL = "https://cbsnooper.com/reports/top-clickbank-products"

class ScrapeResult(BaseModel):
    data: list
    pages_processed: int
    products_count: int

@app.get("/", response_model=str)
async def index():
    return "<h1>Welcome to the Scrape Ninja App</h1>"

@app.get("/scrape", response_model=ScrapeResult)
async def scrape_data():
    client = await async_login_to_cbsnooper_and_transfer_session()
    if client is None:
        raise HTTPException(status_code=401, detail="Login failed")

    data, pages_processed = await parse_all_pages_requests(client, URL)
    result = ScrapeResult(
        data=data,
        pages_processed=pages_processed,
        products_count=len(data)
    )
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8080)
