# exec.py
import asyncio
from scrape import parse_all_pages_requests, save_to_json
from httpx import AsyncClient

async def main():
    base_url = "https://cbsnooper.com/reports/top-clickbank-products"
    async with AsyncClient() as client:
        products = await parse_all_pages_requests(client, base_url)
        if products:
            save_to_json(products)
            print(f"{len(products)} produtos foram encontrados e salvos.")
        else:
            print("Nenhum produto foi encontrado.")

if __name__ == "__main__":
    asyncio.run(main())
