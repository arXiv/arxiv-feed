"""Serializer for Atom 1.0."""

from typing import Tuple
from datetime import datetime
from feedgen.feed import FeedGenerator
from flask import url_for
from arxiv import status
from pytz import utc
from elasticsearch_dsl.response import Response
from rss.serializers.serializer import Serializer
from rss.serializers.atom_extensions import ArxivEntryExtension, ArxivExtension


class Atom_1_0(Serializer): # pylint: disable=too-few-public-methods
    """RSS serializer that produces XML results in the Atom v1.0 format."""

    def get_xml(self: Serializer, response: Response) -> Tuple[str, int]:
        """
        Serialize the provided response data into Atom, version 1.0.

        Parameters
        ----------
        response : Response
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
        archive = response.hits[0]["primary_classification"]["archive"]
        fg.title(archive["id"] + " updates on arXiv.org")
        fg.link(href='http://arxiv.org/rss/version=atom_1.0', rel='self',
                type='application/atom+xml')
        fg.updated(datetime.utcnow().replace(tzinfo=utc))

        # TODO - Try to remove generator element?  This doesn't work - code ignores "None"
        # fg.generator(None)
        # TODO - We don't currently set "subtitle", but could do it like this
        # fg.subtitle(
        #     f"{archive['name']} ({archive['id']}) updates on the arXiv.org e-print archive")

        # Add each search result "hit" to the feed
        for hit in response:
            entry = fg.add_entry()
            entry.id("http://arxiv.org/abs/"+hit['id'])
            entry.title(hit['title'])
            entry.summary(hit['abstract'])
            entry.published(hit['submitted_date'])
            entry.updated(hit['updated_date'])

            entry.link({"href": url_for("abs_by_id", paper_id=hit['id']), "type": "text/html"})
            pdf_link = {"title": "pdf", "rel": "related", "type": "application/pdf"}
            pdf_link["href"] = url_for("pdf_by_id", paper_id=hit['id'])
            entry.link(pdf_link)

            # Add categories
            categories = [hit['primary_classification'].to_dict()['category']]
            for dict in hit['secondary_classification']:
                categories += [dict['category'].to_dict()]
            for cat in categories:
                label = cat['name'] + " (" + cat['id'] + ")"
                category = {"term": cat['id'],
                            "scheme": "http://arxiv.org/schemas/atom",
                            "label": label}
                entry.category(category)

            # Add arXiv-specific element "comment"
            if not hit['comments'].strip():
                entry.arxiv.comment(hit['comments'])

            # Add arXiv-specific element "journal_ref"
            if not hit['journal_ref'].strip():
                entry.arxiv.journal_ref(hit['journal_ref'])

            # Add arXiv-specific element "primary_category"
            prim_cat = hit['primary_classification'].to_dict()['category']
            label = prim_cat['name'] + " (" + prim_cat['id'] + ")"
            category = {"term": prim_cat['id'],
                        "scheme": "http://arxiv.org/schemas/atom",
                        "label": label}
            entry.arxiv.primary_category(category)

            # Add arXiv-specific element "doi"
            if hit['doi']:
                entry.arxiv.doi(hit['doi'])

            # Add each author
            for author in hit['authors']:
                author_list = {"name": author['full_name']}
                entry.author(author_list)
                # TODO - How can arxiv-specific affiliation elements be added to authors?

        data = fg.atom_str(pretty=True)
        status_code = status.HTTP_200_OK
        return data, status_code
