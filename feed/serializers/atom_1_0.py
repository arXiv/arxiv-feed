"""Serializer for Atom 1.0."""

from datetime import datetime

from pytz import utc
from flask import current_app
from feedgen.feed import FeedGenerator

from feed.domain import DocumentSet
from feed.serializers.serializer import Serializer
from feed.serializers.atom_extensions import (
    ArxivEntryExtension,
    ArxivExtension,
)


class Atom10(Serializer):  # pylint: disable=too-few-public-methods
    """RSS serializer that produces XML results in the Atom v1.0 format."""

    def get_feed(self: Serializer, documents: DocumentSet) -> str:
        """
        Serialize the provided response data into Atom, version 1.0.

        Parameters
        ----------
        documents : DocumentSet
            The search response data to be serialized.

        Returns
        -------
        data : str
            The serialized XML results.

        """
        base_server = current_app.config.get("BASE_SERVER")
        urls = current_app.config.get("URLS")

        fg = FeedGenerator()
        fg.register_extension(
            "arxiv", ArxivExtension, ArxivEntryExtension, rss=False
        )
        fg.id(f"https://{base_server}/atom")
        fg.title(f"{', '.join(documents.categories)} updates on arXiv.org")
        fg.link(
            href=f"http://{base_server}/atom",
            rel="self",
            type="application/atom+xml",
        )
        fg.updated(datetime.utcnow().replace(tzinfo=utc))
        fg.generator("")

        # TODO - We don't currently set "subtitle", but could do it like this
        # fg.subtitle(str.join(', ', document.categories) + " updates on the
        # arXiv.org e-print archive")

        # Add each search result to the feed
        for document in documents.documents:
            entry = fg.add_entry()
            entry.id(urls["abs_by_id"].format(paper_id=document.paper_id))
            entry.title(document.title)
            entry.summary(document.abstract)
            entry.published(document.submitted_date)
            entry.updated(document.updated_date)

            entry.link(
                {
                    "type": "text/html",
                    "href": urls["abs_by_id"].format(
                        paper_id=document.paper_id
                    ),
                }
            )
            entry.link(
                {
                    "title": "pdf",
                    "rel": "related",
                    "type": "application/pdf",
                    "href": urls["pdf_by_id"].format(
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
                    "scheme": f"https://{base_server}/schemas/atom",
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
                "scheme": f"https://{base_server}/schemas/atom",
                "label": label,
            }
            entry.arxiv.primary_category(category)

            # Add arXiv-specific element "doi"
            if document.doi:
                entry.arxiv.doi(document.doi)

            # Add each author
            for author in document.authors:
                author_list = {"name": author.full_name}
                entry.author(author_list)
                if len(author.affiliations) > 0:
                    entry.arxiv.affiliation(
                        author.full_name, author.affiliations
                    )

        results: str = fg.atom_str(pretty=True).decode("utf-8")
        return results
