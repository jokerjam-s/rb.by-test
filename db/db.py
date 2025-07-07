"""Управление БД."""
from sqlmodel import create_engine, SQLModel, Session
from settings import AppSettings

from schemas import Category, Product

connect_args = {"check_same_thread": False}
engine = create_engine(AppSettings.SQLite_URL, connect_args=connect_args, echo=False)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    session = Session(bind=engine)
    return session


async def clear_tables():
    """
    Очистка таблиц базы данных.
    :return:
    """
    with get_session() as session:
        session.query(Product).delete()
        session.query(Category).delete()


async def fill_categories(categories: list[Category]):
    """
    Заполняет таблицу категорий новыми значениями,
    :param categories: Новый список категорий
    :return:
    """
    with get_session() as session:
        session.add_all(categories)
        session.commit()


async def fill_products(products: list[Product]):
    """
    Заполняет таблицу товаров новыми значениями,
    :param products: Новый список товаров
    :return:
    """
    with get_session() as session:
        session.add_all(products)
        session.commit()
