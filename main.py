from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from unicodedata import category

from settings import app_settings
from db import create_db_and_tables, SessionDep
from parser import get_list_categories, get_categories

app = FastAPI()

USER_MESSAGE = 'Ok'

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Load the ML model
#     create_db_and_tables()
#     yield
#     # Clean up the ML models and release the resources


@app.on_event("startup")
async def on_startup():
    create_db_and_tables()
    try:
        categories_wb = await get_list_categories(app_settings.CATEGORIES_URL)
        categories = await get_categories(categories_wb)
        print(categories)
    except RuntimeError as e:
        USER_MESSAGE = str(e)



@app.get("/")
async def root():
    return {"Hello": USER_MESSAGE}


@app.get("/health")
async def health():
    return {"message": "Hello, i'm fine. How are you?"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
