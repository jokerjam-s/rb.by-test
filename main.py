import uvicorn
from aiohttp import ClientSession
from fastapi import FastAPI

from settings import AppSettings
from db import create_db_and_tables, fill_categories, fill_products
from parser import load_list_categories, load_categories, load_products

app = FastAPI()
_RESULT_MESSAGE = []


@app.get("/")
async def root():
    return "Перейдите на /start для запуска сбора информации."


@app.get("/start")
async def start():
    create_db_and_tables()
    async with ClientSession() as sessionHttp:
        try:
            categories_wb = await load_list_categories(AppSettings.CATEGORIES_URL, sessionHttp)
            categories = await load_categories(categories_wb)
        except Exception as e:
            _RESULT_MESSAGE.append(e)
        else:
            await fill_categories(categories)

            for category in categories:
                products = []
                page_no = 1
                running = True
                while running:
                    try:
                        url = f'https://catalog.wb.ru/catalog/{category.shardKey}/v2/catalog?ab_testing=false&appType=1&cat={category.id}&dest=-3628814&hide_dtype=13&lang=ru&page={page_no}'
                        products_wb = await load_list_categories(url, sessionHttp)
                        prods = await load_products(products_wb, category)
                        products.extend(prods)
                        page_no += 1
                        print(page_no)
                    except Exception as e:
                        _RESULT_MESSAGE.append(e)
                        running = False
                await fill_products(products)

    return {"Result": _RESULT_MESSAGE}


@app.get("/health")
async def health():
    return {"message": "Hello, i'm fine. How are you?"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
