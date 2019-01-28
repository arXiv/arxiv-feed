"""Serializer for RSS 2.0"""

from typing import Tuple, Optional
from arxiv import status
from rss.serializers.serializer import Serializer
from elasticsearch_dsl.response import Response
import datetime
from rfeed import *


# rfeed Extensions are used to add namespaces to the rss element.
class Content(rfeed.Extension):
    def get_namespace(self):
        return {"xmlns:content": "http://purl.org/rss/1.0/modules/content/"}


class Taxonomy(rfeed.Extension):
    def get_namespace(self):
        return {"xmlns:taxo": "http://purl.org/rss/1.0/modules/taxonomy/"}


class Syndication(rfeed.Extension):
    def get_namespace(self):
        return {"xmlns:syn": "http://purl.org/rss/1.0/modules/syndication/"}


class Admin(rfeed.Extension):
    def get_namespace(self):
        return {"xmlns:admin": "http://webns.net/mvcb/"}


class Rss_2_0(Serializer):

    # TODO - Where to get correct value for pubDate?
    # TODO - Is it OK to let rfeed add elements for "generator" and "docs"?
    def get_xml(self, response: Response) -> Tuple[Optional[dict], int]:
        """
        Serializes the provided response data into RSS, version 2.0.

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

        # Get the archive info from the first hit.  Is this OK?
        archive = response.hits[0]["primary_classification"]["archive"]
        feed = Feed(
            title=archive["id"] + " updates on arXiv.org",
            link="http://arxiv.org/",
            description=archive["name"] + " (" + archive["id"] + ") updates on the arXiv.org e-print archive",
            language="en-us",
            pubDate=datetime.datetime.now(),
            lastBuildDate=datetime.datetime.now(),
            managingEditor="www-admin@arxiv.org"
        )
        feed.extensions.append(Content())
        feed.extensions.append(Taxonomy())
        feed.extensions.append(Syndication())
        feed.extensions.append(Admin())
        feed.image = Image(url="http://arxiv.org/icons/sfx.gif", title="arXiv.org", link="http://arxiv.org")

        for hit in response:
            descr = "<p>Authors: "
            for author in hit['authors']:
                # TODO - Where do we get links for the authors?
                descr += author['full_name'] + ", "
            descr += "</p><p>" + hit['abstract'] + "</p>"
            item = Item(
                title=hit['title'],
                link="http://arxiv.org/abs/"+hit['paper_id'],
                description=descr,
                guid=Guid("oai:arXiv.org:"+hit['paper_id'], isPermaLink=False)
            )
            feed.items.append(item)

        data = feed.rss()
        status_code = status.HTTP_200_OK
        return data, status_code
