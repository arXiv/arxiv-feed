import pytest

from feed import utils
from feed.serializers import Feed
from feed.consts import FeedVersion
from feed.errors import FeedVersionError


@pytest.fixture
def content() -> bytes:
    return b"content"


def test_feed_creation(content: bytes):
    feed = Feed(content)
    assert feed.content == content
    assert feed.version == FeedVersion.RSS_2_0
    assert feed.etag == utils.etag(content)
    assert feed.content_type == "application/rss+xml"

    for version in FeedVersion.supported():
        feed = Feed(content=content, version=version)
        assert feed.content == content
        assert feed.version == version
        assert feed.etag == utils.etag(content)
        if version.is_rss:
            assert feed.content_type == "application/rss+xml"
        if version.is_atom:
            assert feed.content_type == "application/atom+xml"


def test_invalid_version_feed_cration(content: bytes):
    # Test invalid version
    for version in FeedVersion:
        if version not in FeedVersion.supported():
            with pytest.raises(FeedVersionError) as excinfo:
                Feed(content=content, version=version)

            ex: FeedVersionError = excinfo.value
            assert ex.version == version
            assert ex.supported == FeedVersion.supported()

    # Test random string
    with pytest.raises(FeedVersionError) as excinfo:
        Feed(content=content, version="invalid")

    ex: FeedVersionError = excinfo.value
    assert ex.version == "invalid"
