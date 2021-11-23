"""Package to provide python back-end scaffolding."""
from ._logging import configure_logging
from ._settings import Settings

__version__ = "0.1.0"

settings = Settings()

configure_logging(settings.log_level)
