"""Domain classes for the RSS feed."""

from typing import List
from dataclasses import dataclass


@dataclass
class Author:
    """Represents an e-print's author."""

    last_name: str
    full_name: str
    initials: str
    affiliations: List[str]


@dataclass
class Category:
    """Represents an arXiv category."""

    id: str
    name: str


@dataclass
class Document:
    """Represents an arXiv e-print."""

    arxiv_id: str
    archive_name: str
    paper_id: str
    title: str
    abstract: str
    submitted_date: str
    updated_date: str
    comments: str
    journal_ref: str
    doi: str

    authors: List[Author]

    primary_category: Category
    secondary_categories: List[Category]
    """The categories under which this document is filed."""


@dataclass
class DocumentSet:
    """A set of :class:`.Document`s for responding to a specific RSS feed."""

    categories: List[str]
    """The categories that were searched to produce these results."""

    documents: List[Document]
    """Data for all the documents that were found by the search."""
