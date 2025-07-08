import json
import threading
from concurrent.futures import ThreadPoolExecutor, wait

import sqlmodel
from requests import Session
from sqlmodel import select
from typing_extensions import Any

from db import fill_products
from exceptions import WB_CATEGORY_ERROR, WB_PRODUCT_ERROR
from schemas import Category, Product

lock = threading.Lock()


def load_list_categories(url: str, session: Session = None) -> list[dict]:
    """
    Чтение списка словарей с категориями товаров с сайта WB.
    :param url: Строка запроса
    :param session: aiohttp сессия ClientSession, по умолч. None - будет создана автоматически
    :return: Список словарей или выброс исключения WB_CATEGORY_ERROR при ошибке получения данных
    """
    result = []
    session = session or Session()

    with session.get(url) as response:
        if response.status_code != 200:
            raise WB_CATEGORY_ERROR
        try:
            result = response.json()
            result = result.get('data')
        except json.decoder.JSONDecodeError:
            raise WB_CATEGORY_ERROR

    return result


def load_categories(data: list[dict[Any, Any]]) -> list[Category]:
    """
    Рекурсивный разбор словаря категорий.
    Забираем только категории с товарами (childrenOnly=False), указывающие на товары.
    :param data: Список словарей для сериализации
    :return: Список категорий (Category)
    """
    result: list[Category] = []
    for item in data:
        if not item.get('childrenOnly'):
            new_category = Category(
                id=item.get('id'),
                name=item.get('name'),
                url=item.get('url'),
                shardKey=item.get('shardKey'),
                query=item.get('query'),
                rawQuery=item.get('rawQuery'),
            )
            result.append(new_category)
        else:
            nodes = item.get('nodes')
            result.extend(load_categories(nodes))
    return result


def load_list_products(url: str, session: Session = None) -> list[dict]:
    """
    Чтение списка словарей товаров c сайта WB.
    :param url: Строка запроса
    :param session: сессия Session, по умолч. None - будет создана автоматически
    :return: Список словарей или выброс исключения WB_PRODUCT_ERROR при ошибке получения данных
    """
    result = []
    session = session or Session()
    with session.get(url) as response:
        if response.status_code != 200:
            raise WB_PRODUCT_ERROR
        else:
            try:
                result = response.json()
                result = result.get('data').get('products')
            except:
                raise WB_PRODUCT_ERROR
    return result


def load_products(data: list[dict[Any, Any]], category: Category) -> list[Product]:
    """
    Разбор словаря товаров.
    :param category: Категория, к которой принадлежат товары
    :param data: Список словарей для сериализации
    :return: Список товаров (Product)
    """
    result: list[Product] = []
    for item in data:
        price = item.get('sizes')[0].get('price')

        new_product = Product(
            id=item.get('id'),
            name=item.get('name'),
            rating=item.get('reviewRating', 0),
            feedbacks=item.get('feedbacks', 0),
            quantity=item.get('totalQuantity', 0),
            category_id=category.id,
            price_basic=price.get('basic', 0),
            price_prod=price.get('product', 0),
            price_total=price.get('total', 0),
            price_log=price.get('logistics', 0),
        )
        result.append(new_product)
    return result


def safe_fill_db(products: list[Product]):
    """
    Сохранение списка товаров в бд с удалением дубликатов.
    :param products:
    :return:
    """
    products_unique = list(set(products))
    with lock:
        fill_products(products_unique)


def load_part_products_to_db(category: Category, session_http: Session = None):
    page = 1
    products = []
    session_http = session_http or Session()
    while True:
        url = f'https://catalog.wb.ru/catalog/{category.shardKey}/v2/catalog?ab_testing=false&appType=1&cat={category.id}&dest=-3628814&hide_dtype=13&lang=ru&page={page}'
        try:
            products_wb = load_list_products(url, session_http)
            prods = load_products(products_wb, category)
            products.extend(prods)
            page += 1
        except Exception as e:
            break

    safe_fill_db(products)


def load_products_to_db(db_session: sqlmodel.Session, session_http: Session = None):
    """
    Загрузка товаров в БД.
    :return:
    """
    with db_session:
        statement = select(Category)
        result = db_session.exec(statement)
        categories = list(result)

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(load_part_products_to_db, c, session_http) for c in categories]
        wait(futures)
