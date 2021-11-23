"""Module that handels crawling the Archillect TV service."""
import logging
from typing import Any, Dict, List, Union

from bs4 import BeautifulSoup
from httpx import get

from .. import settings
from ..database.models.trashtv import TrashTvArchillectData

_LOGGER = logging.getLogger(__name__)


def get_from_archillect() -> List[Dict[str, Any]]:
    """Scrape and parse current data from Archillect."""
    _LOGGER.info("Start crawling.")
    archillect_request = get(settings.archillect_tv_url)
    crawled_data_raw = BeautifulSoup(archillect_request.text, "html.parser")

    if archillect_request.status_code != 200:
        _LOGGER.warning("Could not fetch from Archillect.", extra={"details": archillect_request})
        return []

    crawled_gifs = _extract_html_data(crawled_data_raw)

    return crawled_gifs


def _extract_html_data(crawled_data: BeautifulSoup) -> List[Dict[str, Any]]:
    """Extract gif id & src from crawled html."""
    result = []
    for html_id in settings.archillect_tv_css_ids:
        is_screenbg = html_id == "screenbg"
        css_key = "style" if is_screenbg else "src"

        gif_id_raw = crawled_data.find(id=html_id)
        gif_id = crawled_data.find(id="gifid").contents[0].replace("#", "") if is_screenbg else gif_id_raw["index"]
        gif_link = (
            crawled_data.find(id=html_id)
            .get(css_key)
            .replace("background-image: url(", "")[: -1 if is_screenbg else None]
        )

        result.append({"archillect_id": gif_id, "source_link": gif_link})

    _LOGGER.info("Finished crawling.", extra={"result": result})
    return result


def get_gif_binary(gif: TrashTvArchillectData) -> Union[Dict[str, Any], None]:
    """Download gif file as binary."""
    gif_request = get(str(gif.source_link))

    if gif_request.status_code != 200:
        _LOGGER.warn("Gif could not be requested.", extra={"gif_id": gif.id, "gif_request": gif_request})
        return None

    return {"id": gif.id, "gif_raw_data": gif_request.content}
