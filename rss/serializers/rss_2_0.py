"""Serializer for RSS 2.0"""

from typing import Tuple, Optional
from arxiv import status
from rss.serializers.serializer import Serializer
from elasticsearch_dsl.response import Response
from rfeed import *
from flask import url_for

import datetime


# Rfeed Extensions are used to add namespaces to the rss element.
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


class RSS_2_0(Serializer):

    # TODO - Use the correct value for pubDate
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
        archive_id = archive["id"]
        archive_name = archive["name"]
        feed = Feed(
            title=f"{archive_id} updates on arXiv.org",
            link="http://arxiv.org/",
            description=f"{archive_name} ({archive_id}) updates on the arXiv.org e-print archive",
            language="en-us",
            pubDate=datetime.datetime.now(),
            lastBuildDate=datetime.datetime.now(),
            managingEditor="www-admin@arxiv.org"
        )

        # Remove two elements added by the Rfeed package
        feed.generator = None
        feed.docs = None

        # Add extensions that will show up as attributes of the rss element
        feed.extensions.append(Content())
        feed.extensions.append(Taxonomy())
        feed.extensions.append(Syndication())
        feed.extensions.append(Admin())
        feed.image = Image(url="http://arxiv.org/icons/sfx.gif", title="arXiv.org", link="http://arxiv.org")

        # Add each search result "hit" to the feed
        for hit in response:
            # Add links for each author and the abstract to the description element
            description = "<p>Authors: "
            first = True
            for author in hit['authors']:
                if first:
                    first = False
                else:
                    description += ", "
                name = f"{author['last_name']},+{author['initials'].replace(' ', '+')}"
                description += f"<a href='http://arxiv.org/search/?query={name}&searchtype=author'>"
                description += f"{author['full_name']}</a>"
            description += f"</p><p>{hit['abstract']}</p>"

            # Create the item element for the "hit"
            item = Item(
                title=hit['title'],
                link=url_for("abs_by_id", paper_id=hit['paper_id']),
                # link=f"http://arxiv.org/abs/{hit['paper_id']}",
                description=description,
                guid=Guid(f"oai:arXiv.org:{hit['paper_id']}", isPermaLink=False)
            )
            feed.items.append(item)

        # Print and return the feed content
        data = feed.rss()
        status_code = status.HTTP_200_OK
        return data, status_code
