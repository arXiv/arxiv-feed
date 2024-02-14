from typing import Optional

import pytest
from lxml import etree

from feed.domain import DocumentSet
from feed.consts import FeedVersion
from feed.serializers import serialize, Feed
from feed.errors import FeedError, FeedVersionError


@pytest.fixture
def documents(sample_doc) -> DocumentSet:
    return DocumentSet(categories=["astro-ph"], documents=[sample_doc])


def check_feed(
    feed: Feed,
    version: FeedVersion,
    status_code: int = 200,
    error: Optional[FeedError] = None,
):
    assert feed.version == version
    assert feed.status_code == status_code

    tree = etree.fromstring(feed.content)
    if version.is_rss:
        link: str = tree.findtext("channel/link")
        title: str = tree.findtext("channel/title")
        description: str = tree.findtext("channel/description")
    elif version.is_atom:
        ns = "{http://www.w3.org/2005/Atom}"
        link = tree.findtext(f"{ns}id")
        title = tree.findtext(f"{ns}title")
        description = tree.findtext(f"{ns}subtitle")
    else:
        raise Exception("Unknown format.")

    if error is None:
        assert "arXiv.org" in title
        assert "updates on the arXiv.org" in description
        check_content(tree, version)
    else:
        assert "Feed error for query" in title
        assert error.error == description

def check_content(tree, version: FeedVersion):
    if version.is_rss:
        ns = {'dc': 'http://purl.org/dc/elements/1.1/'}
        title: str=tree.findtext("channel/item/title")
        link: str=tree.findtext("channel/item/link")
        creators: str = tree.findtext("channel/item/dc:creator", namespaces=ns)
        
    if version.is_atom:
        ns = "{http://www.w3.org/2005/Atom}"
        dc="{http://purl.org/dc/elements/1.1/}"
        title: str = tree.findtext(f"{ns}entry/{ns}title")
        link_entry= tree.find(f"{ns}entry/{ns}link")
        link = link_entry.get('href')
        creators=tree.findall(f"{ns}entry/{dc}creator")

    assert "Mysteries" in title
    assert "://arxiv.org/abs" in link and "1234.5678" in link
    assert len(creators)>0

def test_serialize_documents(app, documents):
    for version in FeedVersion.supported():
        feed = serialize(documents, "astro-ph", version=version)
        check_feed(feed, version=version)


def test_serialize_error(app):
    error = FeedError("Some error text.")
    for version in FeedVersion.supported():
        feed = serialize(error, "astro-ph", version=version)
        check_feed(feed, version=version, status_code=400, error=error)


def test_serialize_invalid_version(app, documents):
    for version in [
        v for v in FeedVersion if v not in FeedVersion.supported()
    ]:
        feed = serialize(documents, "astro-ph", version=version)
        check_feed(
            feed,
            version=FeedVersion.RSS_2_0,
            status_code=400,
            error=FeedVersionError(
                version=version, supported=FeedVersion.supported()
            ),
        )
