"""Test crud functionality."""
from pathlib import Path
from typing import Callable, ContextManager, List

import pytest
import respx
from httpx import Response
from sqlalchemy.orm import Session

from archigetter.archicrawler.crud import gif_to_db, save_gif_to_db
from archigetter.database.models.trashtv import TrashTvArchillectData, TrashTvArchillectHistory

MOCK_GIF_URL = "https://some.fake.gif.url.local"


@respx.mock
def test_gif_to_db(
    clean_db_trashtv: Callable[..., ContextManager[None]],
    get_test_session_trashtv: Callable[..., ContextManager[Session]],
    mock_archillect: Callable[..., ContextManager[None]],
) -> None:
    """Test gif insert into db."""
    test_data = [
        {
            "archillect_id": "123",
            "source_link": "test_url_to_gif_screenbg_1",
            "buffer_id": "456",
            "buffer_link": "test_url_to_gif_buffer_1",
        },
    ]

    with clean_db_trashtv(), mock_archillect(test_data), get_test_session_trashtv() as session:
        gif_to_db(session)
        data_in_db = session.query(TrashTvArchillectData).all()

        assert len(data_in_db) == 2

        assert str(data_in_db[0].archillect_id) == test_data[0]["archillect_id"]
        assert data_in_db[0].source_link == test_data[0]["source_link"]

        assert str(data_in_db[1].archillect_id) == test_data[0]["buffer_id"]
        assert data_in_db[1].source_link == test_data[0]["buffer_link"]


@respx.mock
def test_gif_to_db_with_history(
    clean_db_trashtv: Callable[..., ContextManager[None]],
    get_test_session_trashtv: Callable[..., ContextManager[Session]],
    mock_archillect: Callable[..., ContextManager[None]],
) -> None:
    """Test gif insert into db."""
    test_data = [
        {
            "archillect_id": "123",
            "source_link": "test_url_to_gif_screenbg_1",
            "buffer_id": "456",
            "buffer_link": "test_url_to_gif_buffer_1",
        },
    ]

    with clean_db_trashtv(), mock_archillect(test_data), get_test_session_trashtv() as session:
        gif_to_db(session, add_current=True)
        gif = session.query(TrashTvArchillectData).all()
        gif_history = session.query(TrashTvArchillectHistory).all()

        assert len(gif) == 2
        assert len(gif_history) == 2

        assert gif[0].archillect_id == gif_history[0].gif_id == test_data[0]["archillect_id"]
        assert gif[0].source_link == test_data[0]["source_link"]

        assert gif[1].archillect_id == gif_history[1].gif_id == test_data[0]["buffer_id"]
        assert gif[1].source_link == test_data[0]["buffer_link"]


@respx.mock
def test_gif_to_db_id_already_in_db(
    clean_db_trashtv: Callable[..., ContextManager[None]],
    get_test_session_trashtv: Callable[..., ContextManager[Session]],
    mock_archillect: Callable[..., ContextManager[None]],
) -> None:
    """Test gif insert into db."""
    test_data = [
        {
            "archillect_id": "1",
            "source_link": "test_url_to_gif_screenbg_1",
            "buffer_id": "2",
            "buffer_link": "test_url_to_gif_buffer_2",
        },
        {
            "archillect_id": "3",
            "source_link": "test_url_to_gif_screenbg_3",
            "buffer_id": "2",
            "buffer_link": "test_url_to_gif_buffer_2",
        },
    ]

    with clean_db_trashtv(), mock_archillect(test_data), get_test_session_trashtv() as session:
        gif_to_db(session)
        gif_to_db(session)
        data_in_db = session.query(TrashTvArchillectData).all()

        assert len(data_in_db) == 3

        assert data_in_db[0].archillect_id == test_data[0]["archillect_id"]
        assert data_in_db[0].source_link == test_data[0]["source_link"]

        assert data_in_db[1].archillect_id == test_data[0]["buffer_id"] == test_data[1]["buffer_id"]
        assert data_in_db[1].source_link == test_data[0]["buffer_link"] == test_data[1]["buffer_link"]

        assert data_in_db[2].archillect_id == test_data[1]["archillect_id"]
        assert data_in_db[2].source_link == test_data[1]["source_link"]


@respx.mock
def test_gif_to_db_no_data(
    clean_db_trashtv: Callable[..., ContextManager[None]],
    get_test_session_trashtv: Callable[..., ContextManager[Session]],
    mock_archillect: Callable[..., ContextManager[None]],
) -> None:
    """Test gif insert into db."""
    with clean_db_trashtv(), mock_archillect(), get_test_session_trashtv() as session:
        gif_to_db(session)
        data_in_db = session.query(TrashTvArchillectData).all()

        assert len(data_in_db) == 0


@pytest.mark.respx(base_url=MOCK_GIF_URL)
def test_save_gif_to_db(
    clean_db_trashtv: Callable[..., ContextManager[None]],
    get_test_session_trashtv: Callable[..., ContextManager[Session]],
    insert_row_TrashTvArchillectData: Callable[..., List[TrashTvArchillectData]],
    respx_mock: respx.router.MockRouter,
    project_root_tests_path: Path,
) -> None:
    """Test functionality of `get_gif_binary` function."""
    sample_gif = (project_root_tests_path / "data" / "sample.gif").read_bytes()
    respx_mock.get("/gif_1").mock(return_value=Response(200, content=sample_gif))

    test_db_gif_row = TrashTvArchillectData(archillect_id="1", source_link=MOCK_GIF_URL + "/gif_1")

    with clean_db_trashtv(), get_test_session_trashtv() as session:
        insert_row_TrashTvArchillectData(session, [test_db_gif_row])
        save_gif_to_db(session)

        crawled_gif = session.query(TrashTvArchillectData).all()

        assert len(crawled_gif) == 1

        assert crawled_gif[0].gif_raw_data == sample_gif
