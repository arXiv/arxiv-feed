"""Interface to Index Service for RSS feeds."""

import logging
from typing import Iterable, List, Tuple
from datetime import datetime, timedelta
import certifi

from flask import current_app
from elasticsearch import Elasticsearch, ElasticsearchException
from elasticsearch.connection import Urllib3HttpConnection
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.response import Hit

from arxiv import taxonomy
from arxiv.util.authors import parse_author_affil
from feed.utils import utc_now
from feed.errors import FeedIndexerError
from feed.consts import DELIMITER, Format
from feed.domain import Author, Category, Document, DocumentSet, Document2
from feed.database import get_announce_papers
from feed.tables import ArXivUpdate, ArXivMetadata


logger = logging.getLogger(__name__)

# Start monkeypatch of elasticsearch-py's search(), use POST not GET

import elasticsearch.client

def search2(self, index=None, doc_type=None, body=None, params=None):
  if params and 'from_' in params:
    params['from'] = params.pop('from_')
  if doc_type and not index:
    index = '_all'
  tmppath =  elasticsearch.client.utils._make_path(index, doc_type, '_search')
  return self.transport.perform_request('POST', tmppath, params=params, body=body)

elasticsearch.client.Elasticsearch.search = search2

# End monkeypatch


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
        The results of the ElasticSearch search as a collection of Documents.

    """
    documents: List[Document2] = []

    archives,categories = validate_request(query)
    date=datetime(2021, 2, 15)
    days2=5
    records=get_records_from_db(archives,categories,date,days2) #TODO improve date selection

    # Create a Document object for every hit that was found
    for record in records:
        document = create_document2(record)
        documents.append(document)

    return DocumentSet(categories+archives, documents) #TODO return both categories and archives


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

def get_records_from_db(archives: List[str], categories: List[str], current_date_time: datetime, days: int
) -> List[Tuple[ArXivUpdate, ArXivMetadata]]:
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
    records : List[ArxivUpdate]
        A list of entries from the arxiv_updates table that match the parameters

    """
    #start at the start of today
    last_date=current_date_time.replace(hour=0, minute=0, second=0, microsecond=0) #TODO timezone nonsense
    first_date=last_date - timedelta(days=days)
    return get_announce_papers(first_date,last_date, archives, categories)

def get_records_from_indexer(
    request_categories: List[str], date_time: datetime, days: int
) -> List[Hit]:
    """Retrieve all records that match the list of categories and date range.

    Parameters
    ----------
    request_categories : List[str]
        The archives/categories that will be included in the search.
    date_time : datetime
        The end date and time of the window from which records will be
        filtered.
    days : int
        The number of days before the end date/time that identifies the
        beginning of the filter window.

    Returns
    -------
    records : List[Hit]
        A list of Elasticsearch Hit objects that were returned by the query.
        The list is empty when status is 500.

    """
    query_txt="Not yet set"
    try:
        # Compose a query that includes all specified archives
        sub_queries = []
        for category in request_categories:
            if "." in category:
                # Subcategories, like "cs.AI"
                q = Q("match", primary_classification__category__id=category)
            else:
                # Top-level archives, like "cs"
                q = Q("wildcard", primary_classification__category__id=category + ".*",)
            sub_queries.append(q)
        q = Q("bool", should=sub_queries)

        # Connect to the indexer
        conn_params = {
            "host": current_app.config.get("ELASTICSEARCH_HOST"),
            "port": current_app.config.get("ELASTICSEARCH_PORT"),
            "use_ssl": current_app.config.get("ELASTICSEARCH_SSL"),
            "ca_certs": certifi.where(), # for cert error on cloud run
            "http_auth": None,
            "verify_certs": True,
        }
        es = Elasticsearch(
            [conn_params],
            connection_class=Urllib3HttpConnection,
            send_get_body_as="POST",
        )

        # Perform the search, filtering to only return the `days` papers
        # This search may return up to 10,000 items, per the `extra` params.
        start_date = (date_time - timedelta(days=days)).strftime("%Y-%m-%d")
        end_date = date_time.strftime("%Y-%m-%d")
        search_obj = (
            Search(index=current_app.config.get("ELASTICSEARCH_INDEX"))
            .using(es)
            .query(q)
            .filter(
                "range",
                submitted_date={"gte": start_date, "lte": end_date, "format": "date"},
            )
            .extra(from_=0, size=10_000)
        )
        query_txt = str(search_obj.to_dict())
        response: List[Hit] = search_obj.execute()
        return response
    except ElasticsearchException as ex:
        logger.exception(
            "Failed to fetch documents from ElasticSearch: %s\n"
            "Query: %s", ex, query_txt)
        raise FeedIndexerError("Search engine error.")

def create_document2(record:Tuple[ArXivUpdate, ArXivMetadata])->Document2:
    """Copy data from the provided database entires into a new Document and return it.

    Parameters
    ----------
    record : Tuple[ArXivUpdate, ArXivMetadata]
        Models of data from two tables containing data on the update.

    Returns
    -------
    document : Document
        The new object that is created to hold the documents's data

    """
    update, metadata=record
  
    authors=[]
    for author in parse_author_affil(metadata.authors):
        authors.append(Author(author[0],author[1],author[2],author[3:]))

    categories=metadata.abs_categories.split(" ")

    return Document2(    
        arxiv_id=metadata.paper_id,
        version=metadata.version,
        document_id=metadata.document_id,
        title=metadata.title,
        abstract=metadata.abstract,
        authors=authors,
        categories=categories,
        license=metadata.license,
        journal_ref=metadata.journal_ref,
        update_type=update.action
        )

def create_document(record: Hit) -> Document:
    """Copy data from the provided Hit into a new Document and return it.

    Parameters
    ----------
    record : Hit
        The ElasticSearch record from which to take the e-print information.

    Returns
    -------
    document : Document
        The new object that is created to hold the documents's data

    """
    # Collect top-level properties from the hit
    archive = record["primary_classification"]["archive"]

    # Copy the hit data for authors into the EPrint
    authors = []
    for hit_author in record["authors"]:
        authors.append(
            Author(
                last_name=hit_author["last_name"],
                full_name=hit_author["full_name"],
                initials=hit_author["initials"],
                affiliations=(
                    hit_author["affiliation"] if "affiliation" in hit_author else []
                ),
            )
        )

    # Copy the hit data for categories into the EPrint
    category = record["primary_classification"].to_dict()["category"]
    primary_category = Category(category["name"], category["id"])
    secondary_categories = []
    for classification in record["secondary_classification"]:
        category = classification["category"].to_dict()
        secondary_categories.append(Category(category["name"], category["id"]))

    formats = []
    if "formats" in record and isinstance(record["formats"], Iterable):
        # Formats should be added in the order provided by the supported method
        # because they are ordered by importance since RSS generates only the
        # last one.
        available_formats = {fmt.lower() for fmt in record["formats"]}
        for fmt in Format.supported():
            if fmt in available_formats:
                formats.append(fmt)

    # Create the Document and add it to the collection to be returned
    return Document(
        arxiv_id=archive["id"],
        archive_name=archive["name"],
        paper_id=record["paper_id"],
        title=record["title"],
        abstract=record["abstract"],
        submitted_date=record["submitted_date"],
        updated_date=record["updated_date"],
        comments=record["comments"] if "comments" in record else "",
        journal_ref=record["journal_ref"] if "journal_ref" in record else "",
        doi=record["doi"] if "doi" in record else "",
        formats=formats,
        authors=authors,
        primary_category=primary_category,
        secondary_categories=secondary_categories if "secondary_categories" in record else [],
    )

