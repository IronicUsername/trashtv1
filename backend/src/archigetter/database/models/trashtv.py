"""Module to define minimal table models."""
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from sqlalchemy import Column, func
from sqlalchemy.dialects.postgresql import UUID as POSTGRES_UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.types import TIMESTAMP, VARCHAR, LargeBinary, String, TypeDecorator, TypeEngine

Base: Any = declarative_base()


# context on this: https://github.com/dropbox/sqlalchemy-stubs/issues/36#issuecomment-439559139
# tl;dc: just mypy typing
if TYPE_CHECKING:
    IntEngine = TypeDecorator[String]
else:
    IntEngine = TypeDecorator


class AGNOSTIC_UUID(IntEngine):
    """Converts UUID to string before storing to database. Converts string to UUID when retrieving from database.

    nicked from https://gist.github.com/jmatthias/9262225
    """

    impl = TypeEngine
    cache_ok = True

    def load_dialect_impl(self, dialect: Any) -> Any:
        """When using Postgres database, use the Postgres UUID column type. Otherwise, use String column type."""
        if dialect.name == "postgresql":
            return dialect.type_descriptor(POSTGRES_UUID)
        return dialect.type_descriptor(String)

    def process_bind_param(self, value: Any, dialect: Any) -> Any:
        """When using Postgres database, no conversion. Otherwise, convert to string before storing to database."""
        if dialect.name == "postgres":
            return value
        if value is None:
            return value
        return str(value)

    def process_result_value(self, value: Any, dialect: Any) -> Any:
        """When using Postgres database, no conversion. Otherwise, convert to UUID when retrieving from database."""
        if dialect.name == "postgresql":
            return value
        if value is None:
            return value
        return UUID(value)


class TrashTvArchillectData(Base):
    """DB Model for 'TRASH_TV_ARCHILLECT_DATA' db view."""

    __tablename__ = "TRASH_TV_ARCHILLECT_DATA"

    id = Column(AGNOSTIC_UUID(), primary_key=True, default=uuid4)
    archillect_id = Column(String(), unique=True)
    source_link = Column(VARCHAR())
    gif_raw_data = Column(LargeBinary, nullable=True)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())

    played_on_archillect = relationship("TrashTvArchillectHistory")


class TrashTvArchillectHistory(Base):
    """DB Model for 'TRASH_TV_ARCHILLECT_HISTORY' db view."""

    __tablename__ = "TRASH_TV_ARCHILLECT_HISTORY"

    id = Column(AGNOSTIC_UUID(), primary_key=True, default=uuid4)
    gif_id = Column(String, ForeignKey(TrashTvArchillectData.archillect_id))
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())
