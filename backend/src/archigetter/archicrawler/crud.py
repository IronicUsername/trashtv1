"""Module that handels all crud operations concerning the crawling of Archillect."""
import logging
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy.sql import exists

from ..database.models.trashtv import TrashTvArchillectData, TrashTvArchillectHistory
from . import crawler

_LOGGER = logging.getLogger(__name__)


def gif_to_db(session: Session, add_current: Optional[bool] = False) -> None:
    """Add gif to trashtv db."""
    crawled_gifs = crawler.get_from_archillect()

    if not crawled_gifs:
        _LOGGER.warning("No data was written into db.", extra={"crawled_gifs": crawled_gifs})
        return

    # record history of current gifs

    # check if gif already in db. add if not present.
    for gif in crawled_gifs:
        if session.query(exists().where(TrashTvArchillectData.archillect_id == gif["archillect_id"])).scalar():
            _LOGGER.warning("Archillect id already in db.", extra={"gif": gif["archillect_id"]})
            continue
        session.add(TrashTvArchillectData(**gif))

    if add_current:
        session.add_all([TrashTvArchillectHistory(gif_id=gif["archillect_id"]) for gif in crawled_gifs])

    session.commit()
    return


def save_gif_to_db(session: Session) -> None:
    """Save scraped gif binary in db."""
    not_saved_gifs = session.query(TrashTvArchillectData).filter(TrashTvArchillectData.gif_raw_data.is_(None)).all()
    print(not_saved_gifs)
    session.bulk_update_mappings(TrashTvArchillectData, [crawler.get_gif_binary(gif) for gif in not_saved_gifs])
    session.commit()
    return
