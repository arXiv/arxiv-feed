import pytest
from unittest.mock import patch
from werkzeug import Response

from feed.serializers.feed import Feed
from feed.domain import DocumentSet
from feed.consts import FeedVersion



@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture
def documents() -> DocumentSet:
    return DocumentSet(categories=[], documents=[])


@pytest.fixture
def feed_rss() -> Feed:
    return Feed(content=b"content", version=FeedVersion.RSS_2_0)


@pytest.fixture
def feed_atom() -> Feed:
    return Feed(content=b"content", version=FeedVersion.ATOM_1_0)


@patch("feed.routes.controller.get_documents")
@patch("feed.routes.serialize")
def test_routes_ok(
    serialize,
    get_documents,
    client,
    documents: DocumentSet,
    feed_rss: Feed,
    feed_atom: Feed
):
    get_documents.return_value = documents

    for route, feed in [
        ("/rss/cs.LO", feed_rss),
        ("/rss/cs.LO?version=2.0", feed_rss),
        ("/atom/cs.LO", feed_atom),
    ]:
        serialize.return_value = feed
        response: Response = client.get(route)
        get_documents.assert_called_with("cs.LO")
        assert response.status_code == feed.status_code
        assert response.data == feed.content
        assert response.headers["ETag"] == feed.etag
        assert response.headers["Content-Type"] == feed.content_type


@patch("feed.routes.controller.get_documents")
@patch("feed.routes.serialize")
def test_routes_version_override(
    serialize, get_documents, client, documents: DocumentSet, feed_rss: Feed
):
    get_documents.return_value = documents

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
        serialize.return_value = feed_rss

        client.get(route, headers={"VERSION": version})
        get_documents.assert_called_with("cs.LO")
        serialize.assert_called_with(documents, query="cs.LO", version=override)


def test_routes_unsupported_rss(client):
    for route in [
            "/rss/cs.LO?version=1.0",
            "/rss/cs.LO?version=0.91",
            ]:
        resp = client.get(route)
        resp.status_code == 400


def test_routes_bad_rss(client):
    for route in [
            "/rss/cs.LO?version=9999",
            "/rss/cs.LO?version=bogus",
            "/rss/heplat",
            ]:
        resp = client.get(route)
        resp.status_code == 400


def test_base(client):
    for route in [
        "/rss/",
        "/atom/",
        "/rss",
        "/atom",
        "",
        "/",
    ]:
        resp = client.get(route)
        resp.status_code == 200
