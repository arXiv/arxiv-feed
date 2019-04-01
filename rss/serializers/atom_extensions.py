"""Classes derived from the Feedgen extension classes."""

from typing import Dict
from feedgen.ext.base import BaseEntryExtension, BaseExtension
from feedgen.entry import FeedEntry
from feedgen.feed import FeedGenerator
from lxml import etree


class ArxivExtension(BaseExtension):
    """Extension of the Feedgen base class to allow us to define namespaces."""

    def __init__(self: BaseExtension) -> None:
        """Noop initialization."""
        pass

    @staticmethod
    def extend_atom(atom_feed: FeedGenerator) -> FeedGenerator:
        """
        Assign the Atom feed generator to the extension.

        Parameters
        ----------
        atom_feed
            The FeedGenerator to use for Atom results.

        Returns
        -------
        FeedGenerator
            The provided feed generator.

        """
        return atom_feed

    @staticmethod
    def extend_rss(rss_feed: FeedGenerator) -> FeedGenerator:
        """
        Assign the RSS feed generator to the extension.

        Parameters
        ----------
        rss_feed
            The FeedGenerator to use for RSS results.

        Returns
        -------
        FeedGenerator
            The provided feed generator.

        """
        return rss_feed

    @staticmethod
    def extend_ns() -> Dict[str, str]:
        """
        Assign the feed's namespace string.

        Returns
        -------
        str
            The definition string for the "arxiv" namespace.

        """
        return {'arxiv': 'http://arxiv.org/schemas/atom'}


class ArxivEntryExtension(BaseEntryExtension):
    """Extension of the Feedgen base class to allow us to add elements to the Atom output."""

    def __init__(self: BaseEntryExtension):
        """Initialize the member values to all be empty."""
        self.__arxiv_comment = None
        self.__arxiv_primary_category = None
        self.__arxiv_doi = None
        self.__arxiv_affiliation = None
        self.__arxiv_journal_ref = None

    def extend_atom(self: BaseEntryExtension, entry: FeedEntry) -> FeedEntry:
        """
        Add this extension's new elements to the Atom feed entry.

        Parameters
        ----------
        entry
            The FeedEntry to modify.

        Returns
        -------
        FeedEntry
            The modified entry.

        """
        if self.__arxiv_comment:
            comment_element = etree.SubElement(entry, '{http://arxiv.org/schemas/atom}comment')
            comment_element.text = self.__arxiv_comment

        if self.__arxiv_primary_category:
            etree.SubElement(entry, '{http://arxiv.org/schemas/atom}primary_category',
                             attrib=self.__arxiv_primary_category)

        if self.__arxiv_journal_ref:
            journal_ref_element =\
                etree.SubElement(entry, '{http://arxiv.org/schemas/atom}journal_ref')
            journal_ref_element.text = self.__arxiv_journal_ref

        if self.__arxiv_doi:
            for doi in self.__arxiv_doi:
                doi_element = etree.SubElement(entry, '{http://arxiv.org/schemas/atom}doi')
                doi_element.text = doi

        return entry

    @staticmethod
    def extend_rss(entry: FeedEntry) -> FeedEntry:
        """
        Add this extension's new elements to the RSS feed entry.

        Parameters
        ----------
        entry
            The FeedEntry to modify.

        Returns
        -------
        FeedEntry
            The modfied entry.

        """
        return entry

    def comment(self: BaseEntryExtension, text: str) -> None:
        """
        Assign the comment value to this entry.

        Parameters
        ----------
        text
            The new comment text.

        """
        self.__arxiv_comment = text

    def primary_category(self: BaseEntryExtension, text: str) -> None:
        """
        Assign the primary_category value to this entry.

        Parameters
        ----------
        text
            The new primary_category name.

        """
        self.__arxiv_primary_category = text

    def journal_ref(self: BaseEntryExtension, text: str) -> None:
        """
        Assign the journal_ref value to this entry.

        Parameters
        ----------
        text
            The new journal_ref value.

        """
        self.__arxiv_journal_ref = text

    def doi(self: BaseEntryExtension, list: Dict[str, str]) -> None:
        """
        Assign the doi value to this entry.

        Parameters
        ----------
        list
            The new list of DOI assignments.

        """
        self.__arxiv_doi = list
