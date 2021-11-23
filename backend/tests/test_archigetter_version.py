"""Module that test the package end to end."""
from archigetter import __version__


def test_version():
    assert __version__ == "0.1.0"
