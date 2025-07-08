"""Категории товаров"""
import decimal

from sqlmodel import Field, SQLModel, Relationship


class Category(SQLModel, table=True):
    id: int = Field(max_length=10, primary_key=True)
    name: str = Field(index=True)
    shardKey: str = Field(nullable=True)
    rawQuery: str = Field(nullable=True)
    query: str = Field(nullable=True)
    url: str


class Product(SQLModel, table=True):
    """
    Товары.

    price_basic: базовая стоимость
    price_prod: стоимость единицы продукции
    price_total: общая стоимость
    price_log: расходы на логистику
    rating: рейтинг
    feedbacks: кол-во отзывов
    quantity: количество в наличии
    """
    id: int = Field(max_length=10, nullable=False, primary_key=True)
    name: str = Field(index=True)
    price_basic: decimal.Decimal = Field(nullable=True)
    price_prod: decimal.Decimal = Field(nullable=True)
    price_total: decimal.Decimal = Field(nullable=True)
    price_log: decimal.Decimal = Field(nullable=True)
    rating: decimal.Decimal = Field(nullable=True)
    feedbacks: int = Field(nullable=True)
    quantity: int = Field(nullable=True)
    category_id: int = Field(max_length=10, nullable=True, foreign_key='category.id',primary_key=True)

    # для удаления дубликатов, полученных с WB
    def __eq__(self, other):
        if isinstance(other, Product):
            return self.id == other.id and self.category_id == other.category_id
        return NotImplemented

    def __hash__(self):
        return hash((self.id, self.category_id))

    def __ne__(self, other):
        return self.id != other.id or self.category_id != other.category_id

    def __lt__(self, other):
        return self.id < other.id

    def __gt__(self, other):
        return self.id > other.id

    def __le__(self, other):
        return self.id <= other.id

    def __ge__(self, other):
        return self.id >= other.id