"""Serializer for RSS 2.0."""

from typing import Dict, Tuple
from datetime import datetime
from arxiv import status
from rfeed import Extension, Feed, Guid, Image, Item
from flask import url_for
from rss.serializers.serializer import Serializer
from typing import List

# Rfeed Extensions are used to add namespaces to the rss element.
class Content(Extension):  # pylint: disable=too-few-public-methods
    """
    Adds "content" namespace to RSS output.

    A derivation of the rfeed.Extension class that adds a "content" namespace attribute
    to the top-level RSS element of the output.
    """

    @staticmethod
    def get_namespace() -> Dict[str, str]:
        """
        Return the namespace string for this extension class.

        Returns
        -------
        str
            The string defining the "content" namespace.

        """
        return {"xmlns:content": "http://purl.org/rss/1.0/modules/content/"}


class Taxonomy(Extension):  # pylint: disable=too-few-public-methods
    """
    Adds "taxonomy" namespace to RSS output.

    A derivation of the rfeed.Extension class that adds a "taxonomy" namespace attribute
    to the top-level RSS element of the output.
    """

    @staticmethod
    def get_namespace() -> Dict[str, str]:
        """
        Return the namespace string for this extension class.

        Returns
        -------
        str
            The string defining the "taxonomy" namespace.

        """
        return {"xmlns:taxo": "http://purl.org/rss/1.0/modules/taxonomy/"}


class Syndication(Extension):  # pylint: disable=too-few-public-methods
    """
    Adds "syndication" namespace to RSS output.

    A derivation of the rfeed.Extension class that adds a "syndication" namespace attribute
    to the top-level RSS element of the output.
    """

    @staticmethod
    def get_namespace() -> Dict[str, str]:
        """
        Return the namespace string for this extension class.

        Returns
        -------
        str
            The string defining the "syndication" namespace.

        """
        return {"xmlns:syn": "http://purl.org/rss/1.0/modules/syndication/"}


class Admin(Extension):  # pylint: disable=too-few-public-methods
    """
    Adds "admin" namespace to RSS output.

    A derivation of the rfeed.Extension class that adds a "admin" namespace attribute
    to the top-level RSS element of the output.
    """

    @staticmethod
    def get_namespace() -> Dict[str, str]:
        """
        Return the namespace string for this extension class.

        Returns
        -------
        str
            The string defining the "admin" namespace.

        """
        return {"xmlns:admin": "http://webns.net/mvcb/"}


class RSS_2_0(Serializer):  # pylint: disable=too-few-public-methods
    """RSS serializer that produces XML results in the RSS v2.0 format."""

    # TODO - Use the correct value for pubDate
    def get_xml(self: Serializer, hits: List) -> Tuple[str, int]:
        """
        Serialize the provided response data into RSS, version 2.0.

        Parameters
        ----------
        hits : List
            The search response data to be serialized.

        Returns
        -------
        data : str
            The serialized XML results.
        status
            The HTTP status code for the operation.

        """
        # Get the archive info from the first hit.  Is this OK?
        archive = hits[0]["primary_classification"]["archive"]
        archive_id = archive["id"]
        archive_name = archive["name"]
        feed = Feed(
            title=f"{archive_id} updates on arXiv.org",
            link="http://arxiv.org/",
            description=f"{archive_name} ({archive_id}) updates on the arXiv.org e-print archive",
            language="en-us",
            pubDate=datetime.now(),
            lastBuildDate=datetime.now(),
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
        feed.image = Image(url="http://arxiv.org/icons/sfx.gif",
                           title="arXiv.org", link="http://arxiv.org")

        # Add each search result "hit" to the feed
        for hit in hits:
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
