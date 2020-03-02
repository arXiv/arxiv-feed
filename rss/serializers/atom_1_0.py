"""Serializer for Atom 1.0."""

from datetime import datetime

from pytz import utc
from flask import url_for
from feedgen.feed import FeedGenerator

from rss.domain import DocumentSet
from rss.serializers.serializer import Serializer
from rss.serializers.atom_extensions import ArxivEntryExtension, ArxivExtension


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
        fg = FeedGenerator()
        fg.register_extension(
            "arxiv", ArxivExtension, ArxivEntryExtension, rss=False
        )
        fg.id("http://arxiv.org/rss/version=atom_1.0")
        fg.title(f"{', '.join(documents.categories)} updates on arXiv.org")
        fg.link(
            href="http://arxiv.org/rss/version=atom_1.0",
            rel="self",
            type="application/atom+xml",
        )
        fg.updated(datetime.utcnow().replace(tzinfo=utc))

        # TODO - We don't currently set "subtitle", but could do it like this
        # fg.subtitle(str.join(', ', document.categories) + " updates on the
        # arXiv.org e-print archive")

        # Add each search result to the feed
        for document in documents.documents:
            entry = fg.add_entry()
            entry.id("http://arxiv.org/abs/" + document.paper_id)
            entry.title(document.title)
            entry.summary(document.abstract)
            entry.published(document.submitted_date)
            entry.updated(document.updated_date)

            entry.link(
                {
                    "href": url_for("abs_by_id", paper_id=document.paper_id),
                    "type": "text/html",
                }
            )
            pdf_link = dict(title="pdf", rel="related", type="application/pdf")
            pdf_link["href"] = url_for("pdf_by_id", paper_id=document.paper_id)
            entry.link(pdf_link)

            # Add categories
            categories = [
                document.primary_category
            ] + document.secondary_categories
            for cat in categories:
                label = cat.name + " (" + cat.id + ")"
                category = {
                    "term": cat.id,
                    "scheme": "http://arxiv.org/schemas/atom",
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
                "scheme": "http://arxiv.org/schemas/atom",
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

        results: str = fg.atom_str(pretty=True)
        return results
