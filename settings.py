from pydantic_settings import BaseSettings

__all__ = ['app_settings']


class AppSettings(BaseSettings):
    SQLite_FILE_NAME: str = "wb.db"
    SQLite_URL: str = f"sqlite:///{SQLite_FILE_NAME}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


app_settings = AppSettings()
