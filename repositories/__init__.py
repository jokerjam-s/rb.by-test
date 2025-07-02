# from repositories import

__all__ = ['SessionDep', 'get_session', 'create_db_and_tables']

from typing import Annotated

from sqlmodel import Session

from repositories.db_repository import get_session, create_db_and_tables

SessionDep = Annotated[Session, get_session]
