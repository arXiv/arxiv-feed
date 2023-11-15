"""Domain classes for the RSS feed."""

from typing import List
from dataclasses import dataclass

from feed.consts import Format, UpdateActions


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
class Media:
    """Represents a media item."""

    title: str
    url: str
    format: Format

    @property
    def type(self) -> str:
        if self.format in {Format.PDF, Format.PS}:
            return f"application/{self.format}"
        return "text/html"

@dataclass
class Document:
    """Represents an feed item."""

    arxiv_id: str
    version: int
    document_id:str
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
