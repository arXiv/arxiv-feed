"""Serializer for RSS 2.0."""

from typing import Dict
from datetime import datetime

from flask import current_app
from rfeed import Extension, Feed, Guid, Image, Item

from feed.domain import DocumentSet
from feed.serializers.serializer import Serializer


# Rfeed Extensions are used to add namespaces to the rss element.
class Content(Extension):  # pylint: disable=too-few-public-methods
    """Add "content" namespace to RSS output.

    A derivation of the rfeed.Extension class that adds a "content" namespace
    attribute to the top-level RSS element of the output.
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
    """Add "taxonomy" namespace to RSS output.

    A derivation of the rfeed.Extension class that adds a "taxonomy" namespace
    attribute to the top-level RSS element of the output.
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
    """Adds "syndication" namespace to RSS output.

    A derivation of the rfeed.Extension class that adds a "syndication"
    namespace attribute to the top-level RSS element of the output.
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
    """Add "admin" namespace to RSS output.

    A derivation of the rfeed.Extension class that adds a "admin" namespace
    attribute to the top-level RSS element of the output.
    """

    @staticmethod
    def get_namespace(**kwargs: Dict) -> Dict[str, str]:
        """Return the namespace string for this extension class.

        Returns
        -------
        str
            The string defining the "admin" namespace.

        """
        return {"xmlns:admin": "http://webns.net/mvcb/"}


class RSS20(Serializer):  # pylint: disable=too-few-public-methods
    """RSS serializer that produces XML results in the RSS v2.0 format."""

    # TODO - Use the correct value for pubDate
    def get_feed(self: Serializer, documents: DocumentSet) -> str:
        """Serialize the provided response data into RSS, version 2.0.

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

        feed = Feed(
            title=f"{', '.join(documents.categories)} updates on arXiv.org",
            link=f"https://{base_server}",
            description=f"{', '.join(documents.categories)} updates on the "
            f"{base_server} e-print archive.",
            language="en-us",
            pubDate=datetime.now(),
            lastBuildDate=datetime.now(),
            managingEditor=f"www-admin@{base_server}",
        )

        # Remove two elements added by the Rfeed package
        feed.generator = None
        feed.docs = None

        # Add extensions that will show up as attributes of the rss element
        feed.extensions.append(Content())
        feed.extensions.append(Taxonomy())
        feed.extensions.append(Syndication())
        feed.extensions.append(Admin())
        feed.image = Image(
            url=f"https://{base_server}/icons/sfx.gif",
            title=f"{base_server}",
            link=f"https://{base_server}",
        )

        # Add each search result to the feed
        for document in documents.documents:
            # Add links for each author and the abstract to the description
            # element.
            description = "<p>Authors: "
            first = True
            for author in document.authors:
                if first:
                    first = False
                else:
                    description += ", "
                name = (
                    f"{author.last_name},+{author.initials.replace(' ', '+')}"
                )
                description += (
                    f'<a href="http://{base_server}/search/?'
                    f'query={name}&searchtype=author">{author.full_name}</a>'
                )
            description += f"</p><p>{document.abstract}</p>"

            # Create the item element for the document
            item = Item(
                title=document.title,
                link=urls["abs_by_id"].format(paper_id=document.paper_id),
                description=description,
                guid=Guid(
                    f"oai:arXiv.org:{document.paper_id}", isPermaLink=False
                ),
            )
            feed.items.append(item)

        result: str = feed.rss()
        return result
