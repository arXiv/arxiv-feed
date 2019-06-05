"""Serializer for Atom 1.0."""

from typing import Tuple
from datetime import datetime
from feedgen.feed import FeedGenerator
from flask import url_for
from arxiv import status
from pytz import utc
from rss.serializers.serializer import Serializer
from rss.serializers.atom_extensions import ArxivEntryExtension, ArxivExtension
from typing import List
from rss.domain import Author, EPrint, EPrintSet


class Atom_1_0(Serializer):  # pylint: disable=too-few-public-methods
    """RSS serializer that produces XML results in the Atom v1.0 format."""

    def get_xml(self: Serializer, eprints: EPrintSet) -> Tuple[str, int]:
        """
        Serialize the provided response data into Atom, version 1.0.

        Parameters
        ----------
        eprints : EPrintSet
            The search response data to be serialized.

        Returns
        -------
        data : str
            The serialized XML results.
        status
            The HTTP status code for the operation.

        """
        fg = FeedGenerator()
        fg.register_extension("arxiv", ArxivExtension, ArxivEntryExtension, rss=False)
        fg.id("http://arxiv.org/rss/version=atom_1.0")
        # TODO - Get archive name from somewhere else in case there are no hits
        if len(eprints):
            archive = eprints.eprints[0]
            fg.title(archive.arxiv_id + " updates on arXiv.org")
        fg.link(href='http://arxiv.org/rss/version=atom_1.0', rel='self',
                type='application/atom+xml')
        fg.updated(datetime.utcnow().replace(tzinfo=utc))

        # TODO - Try to remove generator element.  This doesn't work - code ignores "None"
        # fg.generator(None)
        # TODO - We don't currently set "subtitle", but could do it like this
        # fg.subtitle(
        #     f"{archive['name']} ({archive.arxiv_id}) updates on the arXiv.org e-print archive")

        # Add each search result to the feed
        for eprint in eprints.eprints:
            entry = fg.add_entry()
            entry.id("http://arxiv.org/abs/"+eprint.paper_id)
            entry.title(eprint.title)
            entry.summary(eprint.abstract)
            entry.published(eprint.submitted_date)
            entry.updated(eprint.updated_date)

            entry.link({"href": url_for("abs_by_id", paper_id=eprint.paper_id), "type": "text/html"})
            pdf_link = dict(title="pdf", rel="related", type="application/pdf")
            pdf_link["href"] = url_for("pdf_by_id", paper_id=eprint.paper_id)
            entry.link(pdf_link)

            # Add categories
            categories = [eprint.primary_category] + eprint.secondary_categories
            for cat in categories:
                label = cat.name + " (" + cat.id + ")"
                category = {"term": cat.id,
                            "scheme": "http://arxiv.org/schemas/atom",
                            "label": label}
                entry.category(category)

            # Add arXiv-specific element "comment"
            if eprint.comments.strip():
                entry.arxiv.comment(eprint.comments)

            # Add arXiv-specific element "journal_ref"
            if eprint.journal_ref.strip():
                entry.arxiv.journal_ref(eprint.journal_ref)

            # Add arXiv-specific element "primary_category"
            prim_cat = eprint.primary_category
            label = prim_cat.name + " (" + prim_cat.id + ")"
            category = {"term": prim_cat.id,
                        "scheme": "http://arxiv.org/schemas/atom",
                        "label": label}
            entry.arxiv.primary_category(category)

            # Add arXiv-specific element "doi"
            if eprint.doi:
                entry.arxiv.doi(eprint.doi)

            # Add each author
            for author in eprint.authors:
                author_list = {"name": author.full_name}
                entry.author(author_list)
                # TODO - How can arxiv-specific affiliation elements be added to authors?

        data = fg.atom_str(pretty=True)
        status_code = status.HTTP_200_OK
        return data, status_code
