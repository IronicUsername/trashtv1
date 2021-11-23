"""Module that contains settings for the application.

We use `pydantic` to read environment variables.
`pydantic` takes care of settings validation and automatically upercases them
like `cors_allowed_origins` to `CORS_ALLOWED_ORIGINS`.

Settings are set via environmental variables
You need to either
* export environment variables manually - or
* create a `.env` file in the folder you're starting the application from
"""
import logging
import sys
from typing import List

from pydantic import AnyHttpUrl, BaseSettings, validator

_LOGGER = logging.getLogger(__name__)
_HOUR = 60 * 60


class Settings(BaseSettings):
    """Class that contains the application settings."""

    # Only python 3.7 and above support the `dev_mode` flag
    if sys.version_info >= (3, 7):
        is_dev_mode: bool = bool(sys.flags.dev_mode)
    else:
        is_dev_mode: bool = False

    log_level: str = "INFO"

    cors_allowed_origins: List[AnyHttpUrl] = []

    # archillect
    archillect_fetch_period_in_seconds: int = 9
    archillect_tv_url: str = "https://archillect.com/tv"
    archillect_tv_css_ids: List[str] = ["screenbg", "buffer"]

    # db
    db_dsn_trashtv: str = "postgresql://postgres:postgres@localhost:5432/postgres"

    # gif
    # gif_download_period_in_seconds: int = _HOUR  # 1h
    gif_download_period_in_seconds: int = 15  # 1h

    @validator("log_level")
    def check_log_level_name(cls, log_level: str) -> str:
        """Assert that the given log level exists."""
        existing_log_levels = list(logging._nameToLevel)
        if log_level not in existing_log_levels:
            raise ValueError(f'Must provide an existing log level: {", ".join(existing_log_levels)}')

        return log_level

    @validator("cors_allowed_origins")
    def check_cors_allowed_origins(cls, cors_allowed_origins: List[AnyHttpUrl]) -> List[str]:
        """Assert that the given CORS configuration is valid.

        In development/testing, we use `*` per default.

        In production, CORS must not contain `*` (checked via `AnyHttpUrl` type).

        """
        # Only python 3.7 and above support the `dev_mode` flag
        if sys.version_info >= (3, 7) and bool(sys.flags.dev_mode):
            return ["*"]

        if len(cors_allowed_origins) == 0:
            _LOGGER.warning("No CORS whatsoever allowed at the moment!! " "Set `CORS_ALLOWED_ORIGINS` to change this")

        return [str(origin) for origin in cors_allowed_origins]

    class Config:
        """Config of the app settings."""

        env_file = ".env"
        env_file_encoding = "utf-8"
