"""Configure and setup testing of the service."""
from contextlib import AbstractContextManager, contextmanager
from pathlib import Path
from string import Template
from typing import Any, Callable, ContextManager, Dict, Generator, List, Optional

import pytest
import respx
from fastapi.testclient import TestClient
from httpx import Request, Response
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from archigetter import settings
from archigetter.api import app
from archigetter.database.models.trashtv import Base as BasePostgresTrash
from archigetter.database.models.trashtv import TrashTvArchillectData

engine_trashtv = create_engine(settings.db_dsn_trashtv)
SessionLocalTrashTv = sessionmaker(bind=engine_trashtv)


@pytest.fixture(scope="session")
def project_root_path() -> Path:
    """Provide path to project root."""
    return Path(__file__).parent.parent.resolve()


@pytest.fixture(scope="session")
def project_root_tests_path(project_root_path: Path) -> Path:
    """Provide path for tests root."""
    return project_root_path / "tests"


@pytest.fixture(scope="session")
def test_client():
    """Test client of the service.

    [Read here for more](https://fastapi.tiangolo.com/tutorial/testing/)

    """
    return TestClient(app)


def _reset_database_tables(Base, engine):
    Base.metadata.drop_all(bind=engine)


def _initialize_database_tables(Base, engine):
    Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="module")
def clean_db_trashtv() -> Callable[..., AbstractContextManager[None]]:
    """Patch to avoid having data in the trashtv db before and after the test."""

    @contextmanager
    def _clean_db():
        _reset_database_tables(BasePostgresTrash, engine_trashtv)
        _initialize_database_tables(BasePostgresTrash, engine_trashtv)
        yield

        _reset_database_tables(BasePostgresTrash, engine_trashtv)
        return

    return _clean_db


@pytest.fixture(scope="session")
def get_test_session_trashtv() -> Callable[..., AbstractContextManager[sessionmaker]]:
    """Patch to provide a contextmanager for trashtv db session."""

    @contextmanager
    def _get_db_session_trashtv() -> Generator[sessionmaker, None, None]:
        """Get a trashtv db session handle for CRUD, close it automatically once done."""
        db = SessionLocalTrashTv()
        try:
            yield db
        except Exception:
            raise
        else:
            db.commit()
        finally:
            db.close()

    return _get_db_session_trashtv


@pytest.fixture()
def insert_row_TrashTvArchillectData() -> Callable[..., List[TrashTvArchillectData]]:
    """Insert default data for TrashTvArchillectData model."""

    def _insert_data(
        session: Session, batch: Optional[List[TrashTvArchillectData]] = None
    ) -> List[TrashTvArchillectData]:
        if not batch:
            batch = [TrashTvArchillectData(archillect_id="1", source_link="https://test.local")]

        session.add_all(batch)
        session.commit()
        return batch

    return _insert_data


@pytest.fixture()
def mock_archillect_404_html(project_root_tests_path: Path) -> str:
    """Provide html string for 404 html."""
    return (project_root_tests_path / "data" / "sample_archillect_index_404.html").read_text().replace("\n", "")


@pytest.fixture()
def mock_archillect_200_html(project_root_tests_path: Path) -> str:
    """Provide html string for 200 html."""
    return (project_root_tests_path / "data" / "sample_archillect_index_200.html").read_text().replace("\n", "")


@pytest.fixture()
def get_sample_html(mock_archillect_200_html: str, mock_archillect_404_html: str) -> Callable[..., Dict[str, Any]]:
    """Create mock archillect html-string from either default or given data."""

    def _get_sample_html(
        sample_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        if sample_data:
            return {
                "status": 200,
                "html": Template(mock_archillect_200_html).safe_substitute(
                    __UNIQUE_SCREENBG_URL__=sample_data["source_link"],
                    __UNIQUE_BUFFER_ID__=sample_data["buffer_id"],
                    __UNIQUE_BUFFER_URL__=sample_data["buffer_link"],
                    __UNIQUE_SCREENBG_ID__=sample_data["archillect_id"],
                ),
            }

        return {"status": 404, "html": mock_archillect_404_html}

    return _get_sample_html


@pytest.fixture()
async def mock_archillect(
    get_sample_html: Callable[..., Dict[str, Any]],
    mock_archillect_404_html: str,
) -> Callable[..., ContextManager[Dict[str, respx.Route]]]:
    """Mock API for the message API."""

    @contextmanager
    def _mock_archillect(
        sample_data: Optional[List[Dict[str, Any]]] = None
    ) -> Generator[Dict[str, respx.Route], None, None]:
        def _dynamic_message_response(request: Request) -> Response:
            endpoint = str(request.url).split("/")[-1]

            if endpoint != "tv":
                return Response(404, html=mock_archillect_404_html)

            response = get_sample_html(sample_data[len(respx.calls)] if sample_data else None)
            return Response(int(response["status"]), html=response["html"])

        route_archillect = respx.get(url=settings.archillect_tv_url, name="archillect").mock(
            side_effect=_dynamic_message_response
        )
        yield {"archillect": route_archillect}

    return _mock_archillect
