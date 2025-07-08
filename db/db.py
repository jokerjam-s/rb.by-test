"""Управление БД."""
from sqlmodel import create_engine, SQLModel, Session, select

from exceptions import CATEGORY_BY_ID_NOT_EXIST, CATEGORY_BY_NAME_NOT_EXIST
from settings import AppSettings

from schemas import Category, Product

connect_args = {"check_same_thread": False}
engine = create_engine(AppSettings.SQLite_URL, connect_args=connect_args, echo=False)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_db_session():
    session = Session(bind=engine)
    return session


def fill_categories(categories: list[Category]):
    """
    Заполняет таблицу категорий новыми значениями,
    :param categories: Новый список категорий
    :return:
    """
    with get_db_session() as session:
        session.add_all(categories)
        session.commit()


def fill_products(products: list[Product]):
    """
    Заполняет таблицу товаров новыми значениями,
    :param products: Новый список товаров
    :return:
    """
    with get_db_session() as session:
        session.add_all(products)
        session.commit()


def get_products_by_category_id(id: int, offset: int, limit: int) -> list[Product]:
    """
    Получить список товаров по коду категории.
    Если категория с указанным кодом не существует - выброс исключения CATEGORY_BY_ID_NOT_EXIST.
    :param id: Идентификатор категории
    :param offset: Смещение
    :param limit: Количество выбираемых записей
    :return:
    """
    with get_db_session() as session:
        statement = select(Category).where(Category.id == id)
        result = session.exec(statement)
        category = result.first()
        if not category:
            raise CATEGORY_BY_ID_NOT_EXIST

        statement = select(Product).where(Product.category_id == category.id).offset(offset).limit(limit)
        result = session.exec(statement).all()
    result = list(result)
    return result


def get_products_by_category_name(name: str, offset: int, limit: int) -> list[Product]:
    """
    Получить список товаров по категориям соответствующим имени.
    Если категорий не найдено - выброс исключения CATEGORY_BY_NAME_NOT_EXIST.
    :param name: Шаблон имени категории
    :param offset: Смещение
    :param limit: Кол-во выбираемых записей
    :return:
    """
    with get_db_session() as session:
        statement = select(Category).where(Category.name.like(f'%{name}%'))
        result = session.exec(statement).all()
        categories = list(result)
        if len(categories) == 0:
            raise CATEGORY_BY_NAME_NOT_EXIST

        ids = [c.id for c in categories]
        statement = select(Product).where(Product.category_id.in_(ids)).offset(offset).limit(limit)
        result = session.exec(statement).all()

    result = list(result)
    return result


def get_categories():
    """
    Возвращает список всех категорий товаров.
    :return:
    """
    with get_db_session() as db_session:
        statement = select(Category)
        result = db_session.exec(statement).all()

    categories = list(result)
    return categories
