import uvicorn
from fastapi import FastAPI
from requests import Session
from starlette.responses import HTMLResponse, RedirectResponse

from settings import AppSettings
from db import create_db_and_tables, fill_categories, get_db_session, get_products_by_category_id, get_categories, \
    get_products_by_category_name
from parser import load_list_categories, load_categories, load_products_to_db

app = FastAPI()


def make_response(error, data):
    return {'error': error, 'data': data}


@app.get("/", include_in_schema=False)
async def root():
    return HTMLResponse("<a href='/load-data'>Сбор информации с WB.RU</a>.<br>" +
                        "<a href='/show-category-list'>Список категорий</a><br>" +
                        "<a href='/docs'>Swagger API</a>"
                        )


@app.get("/load-data")
async def start():
    """
    Получение списка категорий товаров WB и сохранение их в базе данных.
    """
    create_db_and_tables()
    with Session() as session_http:
        try:
            categories_wb = load_list_categories(AppSettings.CATEGORIES_URL, session_http)
            categories = load_categories(categories_wb)
        except Exception as e:
            return make_response(str(e), [])
        else:
            fill_categories(categories)
            load_products_to_db(get_db_session(), session_http)

    return RedirectResponse('/show-category-list')


@app.get("/show-category-list")
async def show_category_list():
    response = '''<h1>Отобрано категорий</h1>
        <table><thead>
         <tr>
         <th>ID</th> <th>Название</th>
         </tr>
         </thead><tbody>'''

    categories = get_categories()
    for category in categories:
        response += '<tr><td>' + str(category.id) + '</td><td>' + category.name + '</td></tr>'

    response += '</tbody></table>'
    return HTMLResponse(response)


@app.get("/prods-by-category-id")
async def prods_by_category_id(category_id: int, offset: int = 0, limit: int = 100):
    """
    Получение списка товаров, принадлежащих указанной категории в JSON
    """
    try:
        products = get_products_by_category_id(category_id, offset, limit)
    except Exception as e:
        return make_response(str(e), [])

    return make_response('', products)


@app.get("/products-by-category-name")
async def products_by_category_name(category_name: str, offset: int = 0, limit: int = 100):
    """
    Получение списка товаров, попадающих в категории имя которых содержит category_name.
    """
    try:
        products = get_products_by_category_name(category_name, offset, limit)
    except Exception as e:
        return make_response(str(e), [])
    return make_response('', products)


@app.get("/health", include_in_schema=False)
async def health():
    return {"message": "Hello, i'm fine. How are you?"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
