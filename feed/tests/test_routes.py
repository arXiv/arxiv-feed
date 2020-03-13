import pytest
from unittest.mock import patch, MagicMock

from werkzeug import Response

from feed.serializers import Feed
from feed.domain import DocumentSet
from feed.consts import FeedVersion
from feed.errors import FeedVersionError


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


def check_response(response: Response, feed: Feed, get_documents: MagicMock):
    get_documents.assert_called_with("cs.LO")
    assert response.status_code == feed.status_code
    assert response.data == feed.content
    assert response.headers["ETag"] == feed.etag
    assert response.headers["Content-Type"] == feed.content_type


@patch("feed.routes.controller.get_documents")
@patch("feed.routes.serialize")
def test_routes_ok(
    serialize,
    get_documents,
    client,
    documents: DocumentSet,
    feed_rss: Feed,
    feed_atom: Feed,
):
    get_documents.return_value = documents

    for route, feed in [
        ("/cs.LO", feed_rss),
        ("/rss/cs.LO", feed_rss),
        ("/atom/cs.LO", feed_atom),
    ]:
        serialize.return_value = feed
        response: Response = client.get(route)
        check_response(
            response=response, feed=feed, get_documents=get_documents
        )


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
        serialize.assert_called_with(documents, version=override)


@patch("feed.routes.controller.get_documents")
@patch("feed.routes.serialize")
def test_version_ok(
    serialize, get_documents, client, documents: DocumentSet, feed_rss: Feed
):
    get_documents.return_value = documents

    for version in FeedVersion.supported():
        # Return value doesn't matter we just check if the get_feed is called
        # with override FeedVersion
        serialize.return_value = feed_rss

        client.get("/cs.LO", headers={"VERSION": version})
        get_documents.assert_called_with("cs.LO")
        serialize.assert_called_with(documents, version=version)


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
