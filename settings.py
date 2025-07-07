from pydantic_settings import BaseSettings

__all__ = ['AppSettings']


class Settings(BaseSettings):
    SQLite_FILE_NAME: str = "wb.db"
    SQLite_URL: str = f"sqlite:///{SQLite_FILE_NAME}"
    CATEGORIES_URL: str = 'https://catalog.wb.ru/menu/v11/api?locale=by&lang=ru&id=131776&dest=-3628814'

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


AppSettings = Settings()
