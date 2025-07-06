import json
from csv import excel

import aiohttp
from typing_extensions import Any

from exceptions import WB_DATA_ERROR
from schemas import Category


async def get_list_categories(url: str) -> list[dict]:
    """
    Получение списка словарей категорий из json ответа WB gj url.
    Если получить данные не удалось - выброс исключения WB_DATA_ERROR.
    """
    result = {}
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise WB_DATA_ERROR
            try:
                result = await response.json()
            except json.decoder.JSONDecodeError:
                raise WB_DATA_ERROR
    return result


async def get_categories(data: list[dict[Any, Any]]) -> list[Category]:
    """Рекузсивный разбор категорий. Забираем только те для которых установлен query. Остальные не отображаются """
    result: list[Category] = []
    for item in data:
        if item.get('query'):
            new_category = Category(
                name=item.get('seo', item.get('name')),
                url=item.get('url'),
                shard=item.get('shard'),
                parent=item.get('parent'),
                query=item.get('query'),
            )
            result.append(new_category)
            child = item.get('child')
            if child:
                result.extend(await get_categories(child))
    return result
