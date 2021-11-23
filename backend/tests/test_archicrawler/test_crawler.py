"""Test crawling functionality."""
from pathlib import Path
from typing import Callable, ContextManager, List

import pytest
import respx
from httpx import Response
from sqlalchemy.orm import Session

from archigetter.archicrawler.crawler import get_from_archillect, get_gif_binary
from archigetter.database.models.trashtv import TrashTvArchillectData

MOCK_GIF_URL = "https://some.fake.gif.url.local"


@respx.mock
def test_get_from_archillect(mock_archillect: Callable[..., ContextManager[None]]) -> None:
    """Test functionality of the `get_from_archillect` function."""
    test_data = [
        {
            "archillect_id": "123",
            "source_link": "test_url_to_gif_screenbg_1",
            "buffer_id": "456",
            "buffer_link": "test_url_to_gif_buffer_1",
        },
    ]

    with mock_archillect(test_data):
        result = get_from_archillect()

        assert len(respx.calls) == len(test_data)

        assert len(result) == 2

        assert result[0]["archillect_id"] == test_data[0]["archillect_id"]
        assert result[0]["source_link"] == test_data[0]["source_link"]

        assert result[1]["archillect_id"] == test_data[0]["buffer_id"]
        assert result[1]["source_link"] == test_data[0]["buffer_link"]


@respx.mock
def test_get_from_archillect_no_connection(mock_archillect: Callable[..., ContextManager[None]]) -> None:
    """Test functionality of the `get_from_archillect` function."""
    with mock_archillect():
        get_from_archillect()

        assert len(respx.calls) == 1
        assert respx.calls[0].response.status_code == 404


@pytest.mark.respx(base_url=MOCK_GIF_URL)
def test_get_gif_binary(
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
        crawled_gif = get_gif_binary(test_db_gif_row)

        assert crawled_gif

        assert crawled_gif["gif_raw_data"] == sample_gif
