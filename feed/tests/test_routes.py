import pytest
from unittest.mock import patch, MagicMock

from werkzeug import Response

from feed.serializers import Feed
from feed.consts import FeedVersion
from feed.errors import FeedVersionError
from feed.factory import create_web_app


@pytest.fixture
def client():
    app = create_web_app()
    with app.test_client() as client:
        yield client


@pytest.fixture
def feed_rss() -> Feed:
    return Feed(content="content", version=FeedVersion.RSS_2_0)


@pytest.fixture
def feed_atom() -> Feed:
    return Feed(content="content", version=FeedVersion.ATOM_1_0)


def check_response(response: Response, feed: Feed, get_feed: MagicMock):
    get_feed.assert_called_once_with("cs.LO", feed.version)
    assert response.status_code == 200
    assert response.data == feed.content.encode("utf-8")
    assert response.headers["ETag"] == feed.etag
    assert response.headers["Content-Type"] == feed.content_type


def test_routes_ok(client, feed_rss: Feed, feed_atom: Feed):
    for route, feed in [
        ("/cs.LO", feed_rss),
        ("/rss/cs.LO", feed_rss),
        ("/atom/cs.LO", feed_atom),
    ]:
        with patch(
            "feed.routes.controller.get_feed", MagicMock(return_value=feed)
        ) as get_feed:
            response: Response = client.get(route)
            check_response(response=response, feed=feed, get_feed=get_feed)


def test_routes_version_override(client, feed_rss: Feed):
    for version, route, override in [
        # RSS 2.0 override
        (FeedVersion.ATOM_1_0, "/rss/cs.LO", FeedVersion.RSS_2_0),
        (FeedVersion.RSS_0_91, "/rss/cs.LO", FeedVersion.RSS_2_0),
        (FeedVersion.RSS_1_0, "/rss/cs.LO", FeedVersion.RSS_2_0),
        # Atom 1.0 override
        (FeedVersion.RSS_0_91, "/atom/cs.LO", FeedVersion.ATOM_1_0),
        (FeedVersion.RSS_1_0, "/atom/cs.LO", FeedVersion.ATOM_1_0),
        (FeedVersion.RSS_2_0, "/atom/cs.LO", FeedVersion.ATOM_1_0),
    ]:
        # Return value doesn't matter we just check if the get_feed is called
        # with override FeedVersion
        with patch(
            "feed.routes.controller.get_feed", MagicMock(return_value=feed_rss)
        ) as get_feed:
            client.get(route, headers={"VERSION": version})
            get_feed.assert_called_with("cs.LO", override)


def test_version_ok(client, feed_rss: Feed):
    for version in FeedVersion.supported():
        # Return value doesn't matter we just check if the get_feed is called
        # with override FeedVersion
        with patch(
            "feed.routes.controller.get_feed", MagicMock(return_value=feed_rss)
        ) as get_feed:
            client.get("/cs.LO", headers={"VERSION": version})
            get_feed.assert_called_once_with("cs.LO", version)


def test_version_fail(client):
    for version in [
        v for v in FeedVersion if v not in FeedVersion.supported()
    ]:
        feed_version_error = FeedVersionError(
            version=version, supported=FeedVersion.supported()
        )
        response = client.get("/cs.LO", headers={"VERSION": version})
        assert response.status_code == 400
        assert feed_version_error.error in response.data.decode("utf-8")
