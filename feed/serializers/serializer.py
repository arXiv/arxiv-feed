from typing import Dict, Any

from flask import current_app
from feedgen.feed import FeedGenerator

from feed.utils import utc_now
from feed.consts import FeedVersion
from feed.errors import FeedVersionError
from feed.domain import Document, DocumentSet
from feed.serializers import Feed
from feed.serializers.extensions import (
    ArxivExtension,
    ArxivAtomExtension,
    ArxivEntryExtension,
)


class Serializer:
    """Atom 1.0 and RSS 2.0 serializer."""

    def __init__(
        self,
        documents: DocumentSet,
        version: FeedVersion = FeedVersion.RSS_2_0,
    ):
        """Initialize serializer.

        Parameters
        ----------
        documents : DocumentSet
            The search response data to be serialized.
        version : FeedVersion
            Serialization format.

        Raises
        ------
        FeedVersionError
            If the feed serialization format is not supported.
        """
        # Check if the serialization format is supported
        if version not in FeedVersion.supported():
            raise FeedVersionError(
                version=version, supported=FeedVersion.supported()
            )

        # Config data
        self.base_server = current_app.config["BASE_SERVER"]
        self.urls: Dict[str, Any] = current_app.config["URLS"]

        self.version = version
        self.link = (
            f"https://{self.base_server}/atom"
            if version == FeedVersion.ATOM_1_0
            else f"https://{self.base_server}/rss"
        )
        self.content_type = (
            "application/atom+xml"
            if version == FeedVersion.ATOM_1_0
            else "application/rss+xml"
        )

        self.fg = FeedGenerator()

        # Register extensions
        self.fg.register_extension(
            "arxiv", ArxivExtension, ArxivEntryExtension
        )
        self.fg.register_extension("arxiv_atom", ArxivAtomExtension, rss=False)

        # Populate the feed
        self.fg.id(self.link)
        self.fg.link(
            href=self.link, rel="self", type=self.content_type,
        )
        self.fg.image(
            url=f"https://{self.base_server}/icons/sfx.gif",
            title=self.base_server,
            link=self.link,
        )
        self.fg.title(
            f"{', '.join(documents.categories)} updates on arXiv.org"
        )
        self.fg.description(
            f"{', '.join(documents.categories)} updates on the "
            f"{self.base_server} e-print archive.",
        )
        # Timestamps
        now = utc_now()
        self.fg.pubDate(now)
        self.fg.updated(now)

        self.fg.language("en-us")
        self.fg.managingEditor(f"www-admin@{self.base_server}")
        self.fg.generator("")

        # Add each search result to the feed
        for document in documents.documents:
            self.add_document(document)

    def add_document(self, document: Document) -> None:
        """Add document to the feed.

        Parameters
        ----------
        document : Document
            Document that should be added to the feed.
        """
        entry = self.fg.add_entry()
        entry.id(self.urls["abs_by_id"].format(paper_id=document.paper_id))
        entry.guid(f"oai:arXiv.org:{document.paper_id}", permalink=False)
        entry.title(document.title)
        entry.summary(document.abstract)
        entry.published(document.submitted_date)
        entry.updated(document.updated_date)

        entry.link(
            {
                "type": "text/html",
                "href": self.urls["abs_by_id"].format(
                    paper_id=document.paper_id
                ),
            }
        )
        entry.link(
            {
                "title": "pdf",
                "rel": "related",
                "type": "application/pdf",
                "href": self.urls["pdf_by_id"].format(
                    paper_id=document.paper_id
                ),
            }
        )

        # Add categories
        categories = [
            document.primary_category
        ] + document.secondary_categories
        for cat in categories:
            label = cat.name + " (" + cat.id + ")"
            category = {
                "term": cat.id,
                "scheme": f"https://{self.base_server}/schemas/atom",
                "label": label,
            }
            entry.category(category)

        # Add arXiv-specific element "comment"
        if document.comments.strip():
            entry.arxiv.comment(document.comments)

        # Add arXiv-specific element "journal_ref"
        if document.journal_ref.strip():
            entry.arxiv.journal_ref(document.journal_ref)

        # Add arXiv-specific element "primary_category"
        prim_cat = document.primary_category
        label = prim_cat.name + " (" + prim_cat.id + ")"
        category = {
            "term": prim_cat.id,
            "scheme": f"https://{self.base_server}/schemas/atom",
            "label": label,
        }
        entry.arxiv.primary_category(category)

        # Add arXiv-specific element "doi"
        if document.doi:
            entry.arxiv.doi(document.doi)

        # Add authors
        for author in document.authors:
            entry.author({"name": author.full_name})
            entry.arxiv.author(author)
            if len(author.affiliations) > 0:
                entry.arxiv.affiliation(author.full_name, author.affiliations)

    def serialize(self) -> Feed:
        """
        Serialize feed as RSS 2.0.

        Returns
        -------
        Feed
            Feed object containing rss feed.

        Raises
        ------
        FeedVersionError
            If the feed serialization format is not supported.
        """
        if self.version == FeedVersion.RSS_2_0:
            content: bytes = self.fg.rss_str(pretty=True)
        elif self.version == FeedVersion.ATOM_1_0:
            content = self.fg.atom_str(pretty=True)
        else:
            raise FeedVersionError(
                version=self.version, supported=FeedVersion.supported()
            )

        return Feed(content=content.decode("utf-8"),)
