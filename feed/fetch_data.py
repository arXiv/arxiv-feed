"""Interface to Index Service for RSS feeds."""
import logging
from typing import List, Tuple
from datetime import timedelta

from arxiv.taxonomy.category import Category, Archive
from arxiv.taxonomy.definitions import ARCHIVES, CATEGORIES, ARCHIVES_ACTIVE
from arxiv.authors import parse_author_affil
from arxiv.db.models import Metadata

from feed.utils import get_arxiv_midnight
from feed.errors import FeedIndexerError
from feed.consts import DELIMITER, UpdateActions
from feed.domain import Author, Document, DocumentSet
from feed.database import get_announce_papers

logger = logging.getLogger(__name__)

def search(query: str, days: int) -> DocumentSet:
    """Search the index for records with the archive ID and dated within 24h.

    Parameters
    ----------
    query : str
        A concatenation of archive/category specifiers separated by delimiter
        characters.
    days : int
        The number of days before the specified time for which to return
        records.

    Returns
    -------
    documents : DocumentSet
        The results as a collection of Documents.

    """
    documents: List[Document] = []
    archives,categories = validate_request(query)
    records=get_records_from_db(archives,categories, days)

    for record in records:
        document = create_document(record)
        documents.append(document)
    
    topics=[]
    for archive in archives:
        topics.append(archive.id)
    for cat in categories:
        topics.append(cat.id)
    return DocumentSet(topics, documents) 

def validate_request(query: str) -> Tuple[List[Archive],List[Category]]:
    """Validate the provided archive/category specification.

    Return a list of its named archives and categories.

    Parameters
    ----------
    query : str
        A concatenation of archive/category specifiers separated by delimiter
        characters.

    Raises
    ------
    RssIndexerError
        If the provided archive string is malformed or specifies an invalid
        archive or category name.

    Returns
    -------
    request_categories : List[Category] and request_archives : List[Archive]
        If validation was as successful, a tuple of a list of archive and category names.
        Otherwise, and empty list.

    """
    # Separate the request string into individual archives/categories
    request_categories = query.split(DELIMITER)


    # Is the syntax of the archive/category specification correct?
    if len(request_categories) == 0 or any(
        len(cat.strip()) == 0 for cat in request_categories
    ):
        raise FeedIndexerError(
            f"Invalid archive specification '{query}'. Correct format is one "
            f"or more archive names delimited by '{DELIMITER}'. Each name can "
            f"be either of the form 'archive' or 'archive.category'. For "
            f"example: 'math+cs.CG' (all from math and only computational "
            f"geometry from computer science)."
        )

    archives: List[Archive]=[]
    categories: List[Category]=[]

    # Are each of the archives and subjects valid?
    for category in request_categories:

        parts = category.split(".")
        if len(parts)>2:
            raise FeedIndexerError(
                f"Bad archive/subject class structure '{category}'. Valid names include an archive, possibly followed by a single period and subject class."
            )
        
        request_arch=parts[0].lower()
        if not request_arch in ARCHIVES:
            raise FeedIndexerError(
                f"Bad archive '{request_arch}'. Valid archive names are: "
                f"{', '.join(ARCHIVES_ACTIVE.keys())}."
            )
        
        if len(parts)==1:
            archives.append(ARCHIVES[request_arch])
        elif len(parts) == 2:
            category_upper=request_arch+"."+parts[1].upper()
            category_lower=request_arch+"."+parts[1].lower()
            if category_upper in CATEGORIES:
                categories.append(CATEGORIES[category_upper])
            elif category_lower in CATEGORIES:
                categories.append(CATEGORIES[category_lower])
            else:
                possible_cats=[]
                for cat in ARCHIVES[request_arch].get_categories():
                    possible_cats.append(cat.id)
                raise FeedIndexerError(
                    f"Bad subject class '{parts[1]}'. Valid subject classes for "
                    f"the archive '{request_arch}' are: {', '.join(possible_cats)}."
                )

    return archives,categories

def get_records_from_db(archives: List[Archive], categories: List[Category], days: int
) -> List[Tuple[UpdateActions, Metadata]]:
    """Retrieve all records that match the list of categories and date range.

    Parameters
    ----------
    archives : List[str]
        The archives that will be included in the search.
    categories : List[str]
        The categories that will be included in the search.
    current_date_time : datetime
        The date and time of the request.
    days : int
        The number of days before the end date that identifies the
        beginning of the filter window.

    Returns
    -------
    each row is a tuple of the AnnounceType literal and the metadata entry

    """
    #start at the start of today
    last_date=get_arxiv_midnight()
    first_date=last_date - timedelta(days=days-1) #-1 for inclusive date bounds
    return get_announce_papers(first_date.date(),last_date.date(), archives, categories)

def create_document(record:Tuple[UpdateActions, Metadata])->Document:
    """Copy data from the provided database entires into a new Document and return it.

    Parameters
    ----------
    record : Tuple[AnnounceTypes, ArXivMetadata]
        type of announcement listing and metadata for article

    Returns
    -------
    document : Document
        The new object that is created to hold the documents's data

    """
    action, metadata=record
  
    authors=[]
    if metadata.authors:
        for author in parse_author_affil(metadata.authors):
            authors.append(Author(author[0],author[1],author[2],author[3:]))

    categories = metadata.abs_categories.split(" ") if metadata.abs_categories else []

    return Document(    
        arxiv_id=metadata.paper_id,
        version=metadata.version,
        title=metadata.title if metadata.title else "",
        abstract=metadata.abstract if metadata.abstract else "",
        authors=authors,
        categories=categories,
        license=metadata.license if metadata.license else "",
        doi=metadata.doi,
        journal_ref=metadata.journal_ref,
        update_type=action
        )