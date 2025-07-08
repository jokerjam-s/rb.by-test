"""Исключения"""

WB_CATEGORY_ERROR = RuntimeError('Не удалось получить/распознать данные о категориях WB!')
WB_PRODUCT_ERROR = RuntimeError('Не удалось получить/распознать все данные о продуктах WB!')

CATEGORY_BY_ID_NOT_EXIST = RuntimeError('Категории с таким ID нет!')
CATEGORY_BY_NAME_NOT_EXIST = RuntimeError('Категорий с таким названием нет!')
