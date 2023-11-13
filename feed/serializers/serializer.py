from typing import Dict, Union

from flask import current_app
from feedgen.feed import FeedGenerator

from feed.utils import utc_now
from feed.consts import FeedVersion
from feed.errors import FeedError, FeedVersionError
from feed.domain import Media, Document2, DocumentSet
from feed.serializers import Feed
from feed.serializers.extensions import (
    ArxivExtension,
    ArxivAtomExtension,
    ArxivEntryExtension,
)


class Serializer:
    """Atom 1.0 and RSS 2.0 serializer."""

    def __init__(self, version: Union[str, FeedVersion]):
        """Initialize serializer.

        Parameters
        ----------
        version : FeedVersion
            Serialization format.

        Raises
        ------
        FeedVersionError
            If the feed serialization format is not supported.
        """
        # Config data
        self.base_server = current_app.config["BASE_SERVER"]
        self.urls: Dict[str, str] = current_app.config["URLS"]

        self.version = FeedVersion.get(version)
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

    def _create_feed_generator(self) -> FeedGenerator:
        """Creates an empty FeedGenerator and adds arxiv extensions."""
        fg = FeedGenerator()

        # Register extensions
        fg.register_extension("arxiv_atom", ArxivAtomExtension, rss=False)
        fg.register_extension("arxiv", ArxivExtension, ArxivEntryExtension)

        # Populate the feed
        fg.id(self.link)
        fg.link(
            href=self.link, rel="self", type=self.content_type,
        )
        fg.image(
            url=f"https://{self.base_server}/icons/sfx.gif",
            title=self.base_server,
            link=self.link,
        )
        return fg

    def _serialize(self, fg: FeedGenerator, status_code: int = 200) -> Feed:
        """Final version check and serialization.

        Parameters
        ----------
        fg : FeedGenerator
            Populated feed generator object.
        status_code : int
            Status of the serialization.

        Returns
        -------
        Feed
            Feed object containing the serialized feed.

        Raises
        ------
        FeedVersionError
            If the version is not supported.
        """
        if self.version == FeedVersion.RSS_2_0:
            content: bytes = fg.rss_str(pretty=True)
        elif self.version == FeedVersion.ATOM_1_0:
            content = fg.atom_str(pretty=True)
        else:
            raise FeedVersionError(
                version=self.version, supported=FeedVersion.supported()
            )

        return Feed(
            content=content, status_code=status_code, version=self.version
        )

    def add_document(self, fg: FeedGenerator, document: Document2) -> None:
        """Add document to the feed.

        Parameters
        ----------
        fg : FeedGenerator
            Feed generator to which the document should be added.
        document : Document
            Document that should be added to the feed.
        """
        entry = fg.add_entry()

        entry.id(self.urls["abs_by_id"].format(paper_id=document.arxiv_id))
        entry.guid(f"oai:arXiv.org:{document.arxiv_id}", permalink=False)
        entry.title(document.title)
        entry.summary(document.abstract)
        #entry.published(document.submitted_date)
        #entry.updated(document.updated_date)
        entry.link(
            {
                "type": "text/html",
                "href": self.urls["abs_by_id"].format(
                    paper_id=document.arxiv_id
                ),
            }
        )

        # Categories
        entry.rights(document.license)
        categories=[]
        for cat in document.categories:
            categories.append({"term": cat})
        entry.category ( categories)
        # for cat in categories:
        #     # label = cat.name + " (" + cat.id + ")"
        #     category = {
        #          "term": cat
        #     #     "scheme": f"https://{self.base_server}/schemas/atom",
        #     #     "label": label,
        #      }
        #     entry.category(category)

        # # Add arXiv-specific element "comment"
        # if document.comments.strip():
        #     entry.arxiv.comment(document.comments)

        # Add arXiv-specific element "journal_ref"
        if document.journal_ref:
            entry.arxiv.journal_ref(document.journal_ref.strip())

        # # Add arXiv-specific element "primary_category"
        # prim_cat = document.primary_category
        # label = prim_cat.name + " (" + prim_cat.id + ")"
        # category = {
        #     "term": prim_cat.id,
        #     "scheme": f"https://{self.base_server}/schemas/atom",
        #     "label": label,
        # }
        # entry.arxiv.primary_category(category)

        # Add arXiv-specific element "doi"
        if document.document_id:
            entry.arxiv.doi(document.document_id)

        # Add authors
        for author in document.authors:
            full_name=author.full_name+author.last_name+author.initials
            entry.author({"name": full_name})
            entry.arxiv.author(author)
            if len(author.affiliations) > 0:
                entry.arxiv.affiliation(full_name, author.affiliations)

    def serialize_documents(self, documents: DocumentSet) -> Feed:
        """Serialize feed from documents.

        Parameters
        ----------
        documents : DocumentSet
            The search response data to be serialized.

        Returns
        -------
        Feed
            Feed object containing rss feed.

        Raises
        ------
        FeedVersionError
            If the feed serialization format is not supported.
        """
        fg = self._create_feed_generator()
        fg.title(f"{', '.join(documents.categories)} updates on arXiv.org")
        fg.description(
            f"{', '.join(documents.categories)} updates on the "
            f"{self.base_server} e-print archive.",
        )
        # Timestamps
        now = utc_now()
        fg.pubDate(now)
        fg.updated(now)

        fg.language("en-us")
        fg.managingEditor(f"www-admin@{self.base_server}")
        fg.generator("")

        # Add each search result to the feed
        for document in documents.documents:
            self.add_document(fg, document)

        return self._serialize(fg)

    def serialize_error(
        self, error: FeedError, status_code: int = 400
    ) -> Feed:
        """Create feed from an error.

        Parameters
        ----------
        error : FeedError
            Error that happened in the system.
        status_code : int
            Status code of the error.

        Returns
        -------
        Feed
            Feed object containing rss feed.
        """
        fg = self._create_feed_generator()

        fg.title(f"Feed error for query: {self.link}")
        fg.description(error.error)
        # Timestamps
        now = utc_now()
        fg.pubDate(now)
        fg.updated(now)

        fg.language("en-us")
        fg.managingEditor(f"www-admin@{self.base_server}")
        fg.generator("")

        return self._serialize(fg, status_code=status_code)


def serialize(
    documents_or_error: Union[DocumentSet, FeedError],
    version: Union[str, FeedVersion] = FeedVersion.RSS_2_0,
) -> Feed:
    """Serialize a document set or an error.

    Parameters
    ----------
    documents_or_error : Union[DocumentSet, FeedError]
        Either a document set or a Feed error object.
    version : FeedVersion
        Serialization format.

    Returns
    -------
    Feed
        Populated feed object.
    """
    try:
        serializer = Serializer(version=version)
        if isinstance(documents_or_error, DocumentSet):
            return serializer.serialize_documents(documents_or_error)
        elif isinstance(documents_or_error, FeedError):
            return serializer.serialize_error(documents_or_error)
        else:
            raise serializer.serialize_error(
                FeedError("Internal Server Error."), status_code=500
            )
    except FeedVersionError as ex:
        serializer = Serializer(version=FeedVersion.RSS_2_0)
        return serializer.serialize_error(ex)
