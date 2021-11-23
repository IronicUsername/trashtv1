"""Test the settings of the service."""
import pytest

from archigetter._settings import Settings


def test_settings_bad_log_level() -> None:
    with pytest.raises(ValueError):
        Settings(log_level="NON_EXISTENT", match="Must provide an existing")

    with pytest.raises(ValueError, match="Must provide an existing"):
        Settings(log_level="info")


def test_settings_cors_allow_star() -> None:
    with pytest.raises(ValueError, match="invalid or missing URL scheme"):
        Settings(cors_allowed_origins=["*"])


def test_settings_correctly() -> None:
    Settings(cors_allowed_origins=["http://example.org"])
