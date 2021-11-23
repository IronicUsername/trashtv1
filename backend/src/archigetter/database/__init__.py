"""Package to communicate with diffrent databases."""
from .connector import get_db_trashtv_session

__all__ = [
    "get_db_trashtv_session",
]
