"""Domain classes for the RSS feed."""

from typing import List
from dataclasses import dataclass

from feed.consts import UpdateActions


@dataclass
class Author:
    """Represents an e-print's author."""

    last_name: str
    full_name: str
    initials: str
    affiliations: List[str]


@dataclass
class Document:
    """Represents an feed item."""

    arxiv_id: str
    version: int
    doi:str
    title: str
    abstract: str
    authors: List[Author]
    categories: List[str]
    license: str
    journal_ref: str
    update_type: UpdateActions

@dataclass
class DocumentSet:
    """A set of :class:`.Document`s for responding to a specific RSS feed."""

    categories: List[str]
    """The categories that were searched to produce these results."""

    documents: List[Document]
    """Data for all the documents that were found by the search."""
