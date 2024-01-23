"""Interface to Index Service for RSS feeds."""
import logging
from typing import List, Tuple, Dict, Literal
from datetime import datetime, timedelta

from arxiv import taxonomy
from arxiv.util.authors import parse_author_affil

from feed.utils import get_arxiv_midnight
from feed.errors import FeedIndexerError
from feed.consts import DELIMITER, UpdateActions
from feed.domain import Author, Document, DocumentSet
from feed.database import get_announce_papers
from feed.tables import ArXivMetadata

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
    
    return DocumentSet(categories+archives, documents) 

def validate_request(query: str) -> Tuple[List[str],List[str]]:
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
    request_categories : List[str] and request_archives : List[str]
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

    archives=[]
    categories=[]

    # Are each of the archives and subjects valid?
    for category in request_categories:
        parts = category.split(".")
        if len(parts)>2:
            raise FeedIndexerError(
                f"Bad archive/subject class structure '{category}'. Valid names include an archive, possibly followed by a single period and subject class."
            )
        if not parts[0].lower() in taxonomy.ARCHIVES:
            raise FeedIndexerError(
                f"Bad archive '{parts[0]}'. Valid archive names are: "
                f"{', '.join(taxonomy.ARCHIVES.keys())}."
            )
        if len(parts)==1:
            archives.append(category.lower())
        if len(parts) == 2:
            category_upper=parts[0].lower()+"."+parts[1].upper()
            category_lower=parts[0].lower()+"."+parts[1].lower()
            if category_upper in taxonomy.CATEGORIES:
                categories.append(category_upper)
            elif category_lower in taxonomy.CATEGORIES:
                categories.append(category_lower)
            else:
                skip = len(parts[0]) + 1
                groups = [
                    key[skip:]
                    for key in taxonomy.CATEGORIES.keys()
                    if key.startswith(parts[0].lower() + ".")
                ]
                raise FeedIndexerError(
                    f"Bad subject class '{parts[1]}'. Valid subject classes for "
                    f"the archive '{parts[0]}' are: {', '.join(groups)}."
                )

    return archives,categories

def get_records_from_db(archives: List[str], categories: List[str], days: int
) -> List[Tuple[UpdateActions, ArXivMetadata]]:
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
    return get_announce_papers(first_date,last_date, archives, categories)

def create_document(record:Tuple[UpdateActions, ArXivMetadata])->Document:
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
    for author in parse_author_affil(metadata.authors):
        authors.append(Author(author[0],author[1],author[2],author[3:]))

    categories=metadata.abs_categories.split(" ")

    return Document(    
        arxiv_id=metadata.paper_id,
        version=metadata.version,
        title=metadata.title,
        abstract=metadata.abstract,
        authors=authors,
        categories=categories,
        license=metadata.license,
        doi=metadata.doi,
        journal_ref=metadata.journal_ref,
        update_type=action
        )