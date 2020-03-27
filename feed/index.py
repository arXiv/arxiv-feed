"""Interface to Index Service for RSS feeds."""

import logging
from typing import List
from datetime import datetime, timedelta

from flask import current_app
from elasticsearch import Elasticsearch, ElasticsearchException
from elasticsearch.connection import Urllib3HttpConnection
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.response import Hit

from arxiv import taxonomy
from feed.utils import utc_now
from feed.consts import DELIMITER
from feed.errors import FeedIndexerError
from feed.domain import Author, Category, Document, DocumentSet


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
        The results of the ElasticSearch search as a collection of Documents.

    """
    documents: List[Document] = []

    request_categories = validate_request(query)

    records = get_records_from_indexer(request_categories, utc_now(), days)

    # Create a Document object for every hit that was found
    for record in records:
        document = create_document(record)
        documents.append(document)

    return DocumentSet(request_categories, documents)


def validate_request(query: str) -> List[str]:
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
    request_categories : List[str]
        If validation was as successful, a list of archive/category names.
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

    # Are each of the archives and subjects valid?
    for category in request_categories:
        parts = category.split(".")
        if not parts[0] in taxonomy.ARCHIVES:
            raise FeedIndexerError(
                f"Bad archive '{parts[0]}'. Valid archive names are: "
                f"{', '.join(taxonomy.ARCHIVES.keys())}."
            )
        if len(parts) == 2 and category not in taxonomy.CATEGORIES:
            skip = len(parts[0]) + 1
            groups = [
                key[skip:]
                for key in taxonomy.CATEGORIES.keys()
                if key.startswith(parts[0] + ".")
            ]
            raise FeedIndexerError(
                f"Bad subject class '{parts[1]}'. Valid subject classes for "
                f"the archive '{parts[0]}' are: {', '.join(groups)}."
            )

    return request_categories


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
    try:
        # Compose a query that includes all specified archives
        sub_queries = []
        for category in request_categories:
            if "." in category:
                # Subcategories, like "cs.AI"
                q = Q("match", primary_classification__category__id=category)
            else:
                # Top-level categories, like "cs"
                q = Q(
                    "wildcard",
                    primary_classification__category__id=category + ".*",
                )
            sub_queries.append(q)
        q = Q("bool", should=sub_queries)

        # Connect to the indexer
        es = Elasticsearch(
            [
                {
                    "host": current_app.config.get("ELASTICSEARCH_HOST"),
                    "port": current_app.config.get("ELASTICSEARCH_PORT"),
                    "use_ssl": current_app.config.get("ELASTICSEARCH_SSL"),
                    "http_auth": None,
                    "verify_certs": True,
                }
            ],
            connection_class=Urllib3HttpConnection,
        )

        # Perform the search, filtering to only return the last day's papers
        start_date = (date_time - timedelta(days=days)).strftime("%Y-%m-%d")
        end_date = date_time.strftime("%Y-%m-%d")
        response: List[Hit] = Search(index="arxiv").using(es).query(q).filter(
            "range",
            submitted_date={
                "gte": start_date,
                "lte": end_date,
                "format": "date",
            },
        ).execute()
        return response

    except ElasticsearchException as ex:
        logger.exception(
            "Failed to fetch documents from ElasticSearch: %s", ex
        )
        raise FeedIndexerError("Search engine error.")


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
                    hit_author["affiliation"]
                    if "affiliation" in hit_author
                    else []
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

    # Create the Document and add it to the collection to be returned
    return Document(
        arxiv_id=archive["id"],
        archive_name=archive["name"],
        paper_id=record["paper_id"],
        title=record["title"],
        abstract=record["abstract"],
        submitted_date=record["submitted_date"],
        updated_date=record["updated_date"],
        comments=record["comments"],
        journal_ref=record["journal_ref"] if "journal_ref" in record else "",
        doi=record["doi"],
        authors=authors,
        primary_category=primary_category,
        secondary_categories=secondary_categories,
    )
