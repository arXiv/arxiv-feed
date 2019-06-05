"""Domain classes for the RSS feed."""

from typing import List, NamedTuple


class Author(NamedTuple):
    """Represents an e-print's author."""

    last_name: str
    full_name: str
    initials: str


class Category(NamedTuple):
    """Represents an arXiv category."""

    name: str
    id: str


class EPrint(NamedTuple):
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

    """The categories under which this eprint is filed."""
    primary_category: Category
    secondary_categories: List[Category]


class EPrintSet(NamedTuple):
    """A set of :class:`.EPrint`s for responding to a specific RSS feed."""

    """The categories that were searched to produce these results."""
    categories: List[str]

    """Data for all the eprints that were found by the search."""
    eprints: List[EPrint]
