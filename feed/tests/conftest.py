import pytest

from feed.factory import create_web_app


@pytest.fixture
def app():
    return create_web_app()
