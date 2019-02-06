from feedgen.ext.base import BaseExtension, BaseEntryExtension
from lxml import etree


class ArxivExtension(BaseExtension):
    def __init__(self):
        pass

    def extend_atom(self, atom_feed):
        return atom_feed

    def extend_rss(self, rss_feed):
        return rss_feed

    def extend_ns(self):
        return {'arxiv': 'http://arxiv.org/schemas/atom'}


class ArxivEntryExtension(BaseEntryExtension):

    def __init__(self):

        self.__arxiv_comment = None
        self.__arxiv_primary_category = None
        self.__arxiv_doi = None
        self.__arxiv_affiliation = None
        self.__arxiv_journal_ref = None

    def extend_atom(self, entry):

        if self.__arxiv_comment:
            comment_element = etree.SubElement(entry, '{http://arxiv.org/schemas/atom}comment')
            comment_element.text = self.__arxiv_comment

        if self.__arxiv_primary_category:
            etree.SubElement(entry, '{http://arxiv.org/schemas/atom}primary_category',
                             attrib=self.__arxiv_primary_category)

        if self.__arxiv_journal_ref:
            journal_ref_element = etree.SubElement(entry, '{http://arxiv.org/schemas/atom}journal_ref')
            journal_ref_element.text = self.__arxiv_journal_ref

        if self.__arxiv_doi:
            for doi in self.__arxiv_doi:
                doi_element = etree.SubElement(entry, '{http://arxiv.org/schemas/atom}doi')
                doi_element.text = doi

        return entry

    def extend_rss(self, entry):
        return entry

    def comment(self, text):
        self.__arxiv_comment = text

    def primary_category(self, text):
        self.__arxiv_primary_category = text

    def journal_ref(self, text):
        self.__arxiv_journal_ref = text

    def doi(self, list):
        self.__arxiv_doi = list
