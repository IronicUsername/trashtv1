"""Test the root API module."""
import pytest
from fastapi.testclient import TestClient


def test_get_example(test_client: TestClient) -> None:
    """Assert that we get an error from the example endpoint."""
    with pytest.raises(NotImplementedError):
        test_client.get("/")
