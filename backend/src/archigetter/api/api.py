"""Module that describes the service's API behaviour."""
import logging
from asyncio import sleep
from random import choice

import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi_utils.tasks import repeat_every
from starlette.middleware.cors import CORSMiddleware

from .. import archicrawler, settings
from ..database import get_db_trashtv_session
from ..database.models import trashtv

_LOGGER = logging.getLogger(__name__)


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def get_example() -> str:
    """Get an example return.

    TODO: Remove this from service.
    """
    _LOGGER.exception("NOT IMPLEMENTED!")
    raise NotImplementedError("This API has not been implemented")


@app.websocket("/trash")
async def get_trash(websocket: WebSocket) -> None:
    """Websocket to yield gif data from the database."""
    _LOGGER.info("trash was requested.")
    fake_response = {"data": choice(range(100))}
    await websocket.accept()
    while True:
        await websocket.send_json(fake_response)
        await sleep(5)


@app.on_event("startup")
@repeat_every(seconds=settings.archillect_fetch_period_in_seconds)
def record_current_gif() -> None:
    """Get periodically newest gifs from Archillect."""
    _LOGGER.info("Executing periodicall task: current gif to db.")

    with get_db_trashtv_session() as trashtv_db_session:
        archicrawler.gif_to_db(trashtv_db_session, add_current=True)


@app.on_event("startup")
@repeat_every(seconds=settings.gif_download_period_in_seconds)
def download_gifs() -> None:
    """Download and save periodically gifs."""
    _LOGGER.info("Executing periodicall task: download gif to db.")

    with get_db_trashtv_session() as trashtv_db_session:
        archicrawler.save_gif_to_db(trashtv_db_session)


@app.on_event("startup")
def create_application_tables() -> None:
    """Create the table of the database our application directly owns."""
    with get_db_trashtv_session() as trashtv_db_session:
        engine_trashtv = trashtv_db_session.get_bind()
        trashtv.Base.metadata.create_all(engine_trashtv)


def start() -> None:
    """Start running package."""
    uvicorn.run("archigetter.api:app", reload=settings.is_dev_mode)
