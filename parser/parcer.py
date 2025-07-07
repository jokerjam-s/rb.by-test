import json
from sys import stderr

from aiohttp import ClientSession
from typing_extensions import Any

from exceptions import WB_CATEGORY_ERROR, WB_PRODUCT_ERROR
from schemas import Category, Product


async def get_list_categories(url: str, session: ClientSession = None) -> list[dict]:
    """
    Получение списка словарей категорий из json ответа WB gj url.
    Если получить данные не удалось - выброс исключения WB_DATA_ERROR.
    """
    result = []
    session = session or ClientSession()

    async with session.get(url) as response:
        if response.status != 200:
            raise WB_CATEGORY_ERROR
        try:
            result = await response.json()
            result = result.get('data')
        except json.decoder.JSONDecodeError:
            raise WB_CATEGORY_ERROR

    return result


async def load_categories(data: list[dict[Any, Any]]) -> list[Category]:
    """
    Рекурсивный разбор категорий.
    Забираем только категории с товарами (childrenOnly=False), указывающие на товары.
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
            result.extend(await load_categories(nodes))
    return result


async def load_products(category: Category, session: ClientSession) -> list[Product]:
    page_no = 1
    products = []
    while page_no < 2:
        url = f'https://catalog.wb.ru/catalog/{category.shardKey}/v2/catalog?ab_testing=false&appType=1&dest=-3628814&hide_dtype=13&lang=ru&page={page_no}'
        async with session.get(url) as response:
            if response.status == 200:
                try:
                    data = await response.json()
                    data = data.get('data').get('products')

                    for item in data:
                        price = item.get('sizes')[0].get('price')

                        products.append(Product(
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
                        ))
                except Exception as e:
                    stderr.write(str(e))
                    raise WB_PRODUCT_ERROR
            else:
                break
            page_no += 1

    return products
