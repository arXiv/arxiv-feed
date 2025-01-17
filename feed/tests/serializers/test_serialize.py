from typing import Optional
from datetime import datetime
import pytest
from lxml import etree

from feed.domain import DocumentSet
from feed.consts import FeedVersion
from feed.serializers.feed import Feed
from feed.serializers.serializer import serialize
from feed.errors import FeedError, FeedVersionError


@pytest.fixture
def documents(sample_doc) -> DocumentSet:
    return DocumentSet(categories=["astro-ph"], documents=[sample_doc])

@pytest.fixture
def jref_documents(sample_doc_jref) -> DocumentSet:
    return DocumentSet(categories=["astro-ph"], documents=[sample_doc_jref])

def check_feed(
    feed: Feed,
    version: FeedVersion,
    status_code: int = 200,
    error: Optional[FeedError] = None,
):
    assert feed.version == version
    assert feed.status_code == status_code

    today=datetime.today()
    tree = etree.fromstring(feed.content)
    if version.is_rss:
        link: str = tree.findtext("channel/link")
        title: str = tree.findtext("channel/title")
        description: str = tree.findtext("channel/description")
        pub_date: str = tree.findtext("channel/pubDate")
        formatted_date = today.strftime('%a, %d %b %Y')
        formatted_date1 =formatted_date+" 00:00:00 -0400"
        formatted_date2 =formatted_date+" 00:00:00 -0500"
        assert pub_date==formatted_date1 or pub_date==formatted_date2

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
    today=datetime.today()
    if version.is_rss:
        ns = {'dc': 'http://purl.org/dc/elements/1.1/'}
        title: str=tree.findtext("channel/item/title")
        link: str=tree.findtext("channel/item/link")
        creators: str = tree.findtext("channel/item/dc:creator", namespaces=ns)
        pub_date: str = tree.findtext("channel/item/pubDate")
        formatted_date = today.strftime('%a, %d %b %Y')
        formatted_date1 =formatted_date+" 00:00:00 -0400"
        formatted_date2 =formatted_date+" 00:00:00 -0500"
        assert pub_date==formatted_date1 or pub_date==formatted_date2
        
    if version.is_atom:
        ns = "{http://www.w3.org/2005/Atom}"
        dc="{http://purl.org/dc/elements/1.1/}"
        title: str = tree.findtext(f"{ns}entry/{ns}title")
        link_entry= tree.find(f"{ns}entry/{ns}link")
        link = link_entry.get('href')
        creators=tree.findall(f"{ns}entry/{dc}creator")
        pub_date: str = tree.findtext(f"{ns}entry/{ns}published")
        assert f"{today.year:04d}-{today.month:02d}-{today.day:02d}T00:00:00-04:00" in pub_date or f"{today.year:04d}-{today.month:02d}-{today.day:02d}T00:00:00-05:00" in pub_date

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

def test_doi_jref(app, jref_documents, documents):
    for version in FeedVersion.supported():
        #rjref and DOI in feed where applicable
        feed1 = serialize(jref_documents, "astro-ph", version=version)
        check_feed(feed1, version=version)
        assert b"<arxiv:journal_reference>Very Impressive Journal</arxiv:journal_reference>" in feed1.content

        #no element where not apllicable
        feed2 = serialize(documents, "astro-ph", version=version)
        check_feed(feed2, version=version)
        assert b"<arxiv:journal_reference>" not in feed2.content
        
def test_announce_type(app, documents):
    for version in FeedVersion.supported():
        feed = serialize(documents, "astro-ph", version=version)
        check_feed(feed, version=version)
        assert b"<arxiv:announce_type>new</arxiv:announce_type>" in feed.content

def test_description_extras(app, documents):
    for version in FeedVersion.supported():
        feed = serialize(documents, "astro-ph", version=version)
        check_feed(feed, version=version)
        assert b"arXiv:1234.5678v3 Announce Type: new \nAbstract:" in feed.content