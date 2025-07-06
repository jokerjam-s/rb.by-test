"""Категории товаров"""
import decimal
from typing import List, Optional

from sqlmodel import Field, SQLModel, Relationship


class Category(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str = Field(index=True)
    shard: str = Field(nullable=True)
    parent: int = Field(nullable=True)
    query: str = Field(nullable=True)
    url: str
    products: List['Product'] = Relationship(back_populates='category')


class Product(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str = Field(index=True)
    price: decimal.Decimal = Field(nullable=True)
    discont_price: decimal.Decimal = Field(nullable=True)
    rate: int = Field(nullable=True)
    rewiev_amount: int = Field(nullable=True)
    category_id: int = Field(nullable=True, foreign_key='category.id')
