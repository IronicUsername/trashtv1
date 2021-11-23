"""Test for the database connection module."""
from typing import Callable, ContextManager

from sqlalchemy.orm import Session


def test_db_connection(
    clean_db_trashtv: Callable[..., ContextManager[None]],
    get_test_session_trashtv: Callable[..., ContextManager[Session]],
) -> None:
    with clean_db_trashtv(), get_test_session_trashtv() as session:
        res = session.execute("select 1").one()
        assert len(res) == 1
        assert res[0] == 1
