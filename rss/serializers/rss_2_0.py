"""Serializer for RSS 2.0."""

from typing import Dict
from datetime import datetime
from rfeed import Extension, Feed, Guid, Image, Item
from flask import url_for
from rss.serializers.serializer import Serializer
from rss.domain import EPrintSet


# Rfeed Extensions are used to add namespaces to the rss element.
class Content(Extension):  # pylint: disable=too-few-public-methods
    """
    Adds "content" namespace to RSS output.

    A derivation of the rfeed.Extension class that adds a "content" namespace attribute
    to the top-level RSS element of the output.
    """

    @staticmethod
    def get_namespace(**kwargs: Dict) -> Dict[str, str]:
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
    def get_namespace(**kwargs: Dict) -> Dict[str, str]:
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
    def get_namespace(**kwargs: Dict) -> Dict[str, str]:
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
    def get_namespace(**kwargs: Dict) -> Dict[str, str]:
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
    def get_xml(self: Serializer, eprints: EPrintSet) -> str:
        """
        Serialize the provided response data into RSS, version 2.0.

        Parameters
        ----------
        eprints : EPrintSet
            The search response data to be serialized.

        Returns
        -------
        data : str
            The serialized XML results.

        """
        feed = Feed(
            title=f"{str.join(', ', eprints.categories)} updates on arXiv.org",
            link="http://arxiv.org/",
            description=f"{str.join(', ', eprints.categories)} updates on the arXiv.org e-print archive",
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

        # Add each search result to the feed
        for eprint in eprints.eprints:
            # Add links for each author and the abstract to the description element
            description = "<p>Authors: "
            first = True
            for author in eprint.authors:
                if first:
                    first = False
                else:
                    description += ", "
                name = f"{author.last_name},+{author.initials.replace(' ', '+')}"
                description += f"<a href='http://arxiv.org/search/?query={name}&searchtype=author'>"
                description += f"{author.full_name}</a>"
            description += f"</p><p>{eprint.abstract}</p>"

            # Create the item element for the eprint
            item = Item(
                title=eprint.title,
                link=url_for("abs_by_id", paper_id=eprint.paper_id),
                # link=f"http://arxiv.org/abs/{hit['paper_id']}",
                description=description,
                guid=Guid(f"oai:arXiv.org:{eprint.paper_id}", isPermaLink=False)
            )
            feed.items.append(item)

        # Print and return the feed content
        results: str = feed.rss()
        return results
