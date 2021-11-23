"""Module to maintain database connection, setup, helpers."""
import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .. import settings

_LOGGER = logging.getLogger(__name__)

engine_trashtv = create_engine(settings.db_dsn_trashtv)


@contextmanager
def _get_db_session(session_local: sessionmaker) -> Generator[Session, None, None]:
    """Create db session handler for various dbs, close it automatically once done."""
    session = session_local()
    try:
        yield session
    except Exception as e:
        _LOGGER.error("Exception occurred while running DB code, attempting rollback", extra={"exception": e})
        session.rollback()
        raise
    else:
        session.commit()
    finally:
        session.close()


@contextmanager
def get_db_trashtv_session() -> Generator[Session, None, None]:
    """Get trashtv db session."""
    SessionLocal = sessionmaker(engine_trashtv)
    with _get_db_session(SessionLocal) as db:
        yield db
