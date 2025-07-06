"""Управление БД."""
from sqlmodel import create_engine, SQLModel, Session
from settings import app_settings

from schemas import Category, Product

connect_args = {"check_same_thread": False}
engine = create_engine(app_settings.SQLite_URL, connect_args=connect_args, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
