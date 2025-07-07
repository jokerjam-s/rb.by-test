from itertools import product
from sys import stderr

import uvicorn
from aiohttp import ClientSession
from fastapi import FastAPI

from settings import AppSettings
from db import create_db_and_tables, get_session
from parser import get_list_categories, load_categories, load_products

app = FastAPI()
RESULT_MESSAGE = 'Ok'


@app.get("/")
async def root():
    return "Перейдите на /start для запуска сбора информации."


@app.get("/start")
async def start():
    create_db_and_tables()
    async with ClientSession() as sessionHttp:
        try:
            categories_wb = await get_list_categories(AppSettings.CATEGORIES_URL, sessionHttp)
            categories = await load_categories(categories_wb)
        except Exception as e:
            stderr.write(str(e))
            RESULT_MESSAGE = f'Ошибка: {e}'
        else:
            sessionDb = get_session()
            for category in categories:
                sessionDb.add(category)
            sessionDb.commit()

            for category in categories:
                try:
                    products = await load_products(category, sessionHttp)
                    for product in products:
                        sessionDb.add(product)
                    sessionDb.commit()
                except Exception as e:
                    sessionDb.rollback()
                    RESULT_MESSAGE = f'Ошибка: {e}'
                    stderr.write(str(e))

            # sessionDb.commit()
    return {"Result": RESULT_MESSAGE}


@app.get("/health")
async def health():
    return {"message": "Hello, i'm fine. How are you?"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
