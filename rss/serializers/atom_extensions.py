"""Classes derived from the Feedgen extension classes."""

from typing import Dict, List
from feedgen.ext.base import BaseEntryExtension, BaseExtension
from lxml import etree
from lxml.etree import Element


class ArxivExtension(BaseExtension):
    """Extension of the Feedgen base class to allow us to modify and extend its behavior."""

    def __init__(self: BaseExtension) -> None:
        """Noop initialization."""
        pass

    def extend_atom(self: BaseExtension, atom_feed: Element) -> Element:
        """
        Allow the extension to modify the initial feed element tree for Atom serialization.

        Parameters
        ----------
        atom_feed : Element
            The feed's root element.

        Returns
        -------
        atom_feed : Element
            The feed's root element.

        """
        # Remove the unwanted "generator" element, which can't be erased though the API.
        for child in atom_feed:
            if child.tag == 'generator':
                atom_feed.remove(child)

        return atom_feed

    def extend_rss(self: BaseExtension, rss_feed: Element) -> Element:
        """
        Allow the extension to modify the initial feed element tree for RSS serialization.

        Parameters
        ----------
        rss_feed : Element
            The feed's root element.

        Returns
        -------
        rss_feed : Element
            The feed's root element.

        """
        return rss_feed

    def extend_ns(self: BaseExtension) -> Dict[str, str]:
        """
        Define the feed's namespaces.

        Returns
        -------
        namespaces : Dict[str, str]
            Definitions of the "arxiv" namespaces.

        """
        return {'arxiv': 'http://arxiv.org/schemas/atom'}


class ArxivEntryExtension(BaseEntryExtension):
    """Extension of the Feedgen Entry base class to allow us to modify and extend its behavior."""

    def __init__(self: BaseEntryExtension):
        """Initialize the member values to all be empty."""
        self.__arxiv_comment: str = None
        self.__arxiv_primary_category: str = None
        self.__arxiv_doi: Dict = None
        self.__arxiv_affiliation: str = None
        self.__arxiv_journal_ref: str = None
        self.__arxiv_affiliations: Dict = {}

    def extend_atom(self, entry: Element) -> Element:
        """
        Allow the extension to modify the entry element for Atom serialization.

        Parameters
        ----------
        entry : Element
            The FeedEntry to modify.

        Returns
        -------
        entry : Element
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

        # Check each of the entry's author nodes
        for entry_child in entry:
            if entry_child.tag == 'author':
                author = entry_child
                for author_child in author:
                    # If the author's name is in the affiliation dictionary, add Elements for all of its affiliations.
                    if author_child.tag == 'name':
                        name = author_child.text
                        affiliations = self.__arxiv_affiliations[name]
                        for affiliation in affiliations:
                            element = etree.SubElement(author, '{http://arxiv.org/schemas/atom}affiliation')
                            element.text = affiliation

        return entry

    def extend_rss(self, entry: Element) -> Element:
        """
        Allow the extension to modify the entry element for RSS serialization.

        Parameters
        ----------
        entry : Element
            The FeedEntry to modify.

        Returns
        -------
        entry : Element
            The modified entry.

        """
        return entry

    def comment(self, text: str) -> None:
        """
        Assign the comment value to this entry.

        Parameters
        ----------
        text : str
            The new comment text.

        """
        self.__arxiv_comment = text

    def primary_category(self, text: str) -> None:
        """
        Assign the primary_category value to this entry.

        Parameters
        ----------
        text : str
            The new primary_category name.

        """
        self.__arxiv_primary_category = text

    def journal_ref(self, text: str) -> None:
        """
        Assign the journal_ref value to this entry.

        Parameters
        ----------
        text : str
            The new journal_ref value.

        """
        self.__arxiv_journal_ref = text

    def doi(self, doi_list: Dict[str, str]) -> None:
        """
        Assign the set of DOI definitions for this entry.

        Parameters
        ----------
        doi_list : Dict[str, str]
            A dictionary of DOI assignments.

        """
        self.__arxiv_doi = doi_list

    def affiliation(self, full_name: str, affiliations: List[str]) -> None:
        """
        Assign an affiliation for one author of this entry.

        Parameters
        ----------
        full_name : str
            An author's full name.
        affiliations : List[str]
            The code for the author's affiliated institution.

        """
        self.__arxiv_affiliations[full_name] = affiliations
