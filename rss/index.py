"""Interface to Index Service for RSS feeds."""

from arxiv import taxonomy
from elasticsearch import Elasticsearch, ElasticsearchException
from elasticsearch.connection import Urllib3HttpConnection
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.response import Hit
import datetime
from typing import List
from .domain import Author, Category, EPrint, EPrintSet

DELIMITER = '+'


class RssIndexerError(Exception):
    """An exception for returning errors from the RSS feed's indexer."""

    def __init__(self, message: str):
        """
        Initialize an exception.

        Parameters
        ----------
        message : str
            The error message for the exception.

        """
        self.message = message


def perform_search(archives: str, date_time: datetime.datetime, days: int) -> EPrintSet:
    """
    Search the index for records with the archive ID and dated within 24 hours of date_time.

    Parameters
    ----------
    archives : str
        The IDs of the archives to search
    date_time : datetime
        The date/time that defines the end of the 24 hour search window.
    days : int
        The number of days before the specified time for which to return records.

    Returns
    -------
    eprints : EPrintSet
        The results of the Elasticsearch search as a collection of EPrints

    """
    eprints: List[EPrint] = list()

    request_categories = validate_request(archives)

    records = get_records_from_indexer(request_categories, date_time, days)

    # Create an EPrint object for every hit that was found
    for record in records:
        eprint = create_eprint(record)
        eprints.append(eprint)

    return EPrintSet(request_categories, eprints)


def validate_request(archives: str) -> List[str]:
    """
    Validate the provided archive/category specification and return a list of its named archives and categories.

    Parameters
    ----------
    archives : str
        A concatenation of archive/category specifiers separated by delimiter characters.

    Raises
    ------
    RssIndexerError
        If the provided archive string is malformed or specifies an invalid archive or category name.

    Returns
    -------
    request_categories : List[str]
        If validation was as successful, a list of archive/category names.  Otherwise, and empty list.

    """
    # Separate the request string into individual archives/categories
    request_categories = archives.split(DELIMITER)

    # Is the syntax of the archive/category specification correct?
    if len(request_categories) == 0 or any(len(cat) == 0 for cat in request_categories):
        msg = "Invalid archive specification '" + archives + "'.  " + \
              "Correct format is one or more archive names delimited by '" + DELIMITER + "'.  " + \
              "Each name can be either of the form 'archive' or 'archive.category'.  " + \
              "For example: 'math+cs.CG' (all from math and only computational geometry from computer science)."
        raise RssIndexerError(msg)

    # Are each of the archives and subjects valid?
    for category in request_categories:
        parts = category.split(".")
        if not parts[0] in taxonomy.ARCHIVES:
            msg = "Bad archive '" + parts[0] + "'.  Valid archive names are: " + \
                  str.join(', ', taxonomy.ARCHIVES.keys()) + "."
            raise RssIndexerError(msg)
        if len(parts) == 2 and category not in taxonomy.CATEGORIES:
            skip = len(parts[0]) + 1
            groups = [key[skip:] for key in taxonomy.CATEGORIES.keys() if key.startswith(parts[0] + '.')]
            msg = "Bad subject class '" + parts[1] + "'.  " + \
                  "Valid subject classes for the archive '" + parts[0] + "' are: " + \
                  str.join(', ', groups) + "."
            raise RssIndexerError(msg)

    return request_categories


def get_records_from_indexer(request_categories: List[str],
                             date_time: datetime.datetime, days: int) -> List[Hit]:
    """
    Retrieve all records from the indexer that match the list of categories and date range.

    Parameters
    ----------
    request_categories : List[str]
        The archives/categories that will be included in the search.
    date_time : datetime.datetime
        The end date and time of the window from which records will be filtered.
    days : int
        The number of days before the end date/time that identifies the beginning of the filter window.

    Returns
    -------
    records : List[Hit]
        A list of Elasticsearch Hit objects that were returned by the query.  The list is empty when status is 500.

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
                q = Q("wildcard", primary_classification__category__id=category + ".*")
            sub_queries.append(q)
        q = Q("bool", should=sub_queries)

        # Connect to the indexer
        es = Elasticsearch([{'host': 'localhost', 'port': 9200,
                             'use_ssl': False,
                             'http_auth': None,
                             'verify_certs': True}],
                           connection_class=Urllib3HttpConnection)

        # Perform the search, filtering to only return the last day's papers
        start_date = (date_time - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
        end_date = date_time.strftime('%Y-%m-%d')
        response: List[Hit] = Search(index='arxiv')\
            .using(es) \
            .query(q) \
            .filter("range", submitted_date={'gte': start_date, 'lte': end_date, 'format': 'date'}) \
            .execute()
        return response

    except ElasticsearchException as e:
        raise RssIndexerError("Search engine error.")


def create_eprint(record: Hit) -> EPrint:
    """
    Copy data from the provided Elasticsearch Hit into a new EPrint object and return it.

    Parameters
    ----------
    record : Hit
        The Elasticsearch record from which to take the e-print information.

    Returns
    -------
    eprint : EPrint
        The new object that is created to hold the e-print's data

    """
    # Collect top-level properties from the hit
    archive = record["primary_classification"]["archive"]
    arxiv_id = archive["id"]
    archive_name = archive["name"]
    paper_id = record['paper_id']
    title = record['title']
    abstract = record['abstract']
    submitted_date = record['submitted_date']
    updated_date = record['updated_date']
    comments = record['comments']
    journal_ref = record['journal_ref']
    doi = record['doi']

    # Copy the hit data for authors into the EPrint
    authors = list()
    for hit_author in record['authors']:
        last_name = hit_author['last_name']
        full_name = hit_author['full_name']
        initials = hit_author['initials']
        author = Author(last_name, full_name, initials)
        authors.append(author)

    # Copy the hit data for categories into the EPrint
    category = record['primary_classification'].to_dict()['category']
    primary_category = Category(category['name'], category['id'])
    secondary_categories = list()
    for classification in record['secondary_classification']:
        category = classification['category'].to_dict()
        secondary_category = Category(category['name'], category['id'])
        secondary_categories.append(secondary_category)

    # Create the EPrint and add it to the collection to be returned
    eprint = EPrint(arxiv_id, archive_name, paper_id, title, abstract,
                    submitted_date, updated_date, comments, journal_ref, doi,
                    authors, primary_category, secondary_categories)

    return eprint
