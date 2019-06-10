"""Interface to Index Service for RSS feeds."""

from elasticsearch import Elasticsearch, ElasticsearchException
from elasticsearch.connection import Urllib3HttpConnection
from elasticsearch_dsl import Search, Q
import datetime
from typing import List
from .domain import Author, Category, EPrint, EPrintSet


def perform_search(archives: str, date_time: datetime.datetime) -> EPrintSet:
    """
    Search the index for records with the archive ID and dated within 24 hours of date_time.

    Parameters
    ----------
    archives : str
        The IDs of the archives to search
    date_time : datetime
        The date/time that defines the end of the 24 hour search window.

    Returns
    -------
    hits : List
        The results of the Elasticsearch search as a list of .

    """
    request_categories: List[str] = list()
    eprints: List[EPrint] = list()

    try:
        es = Elasticsearch([{'host': 'localhost', 'port': 9200,
                             'use_ssl': False,
                             'http_auth': None,
                             'verify_certs': True}],
                           connection_class=Urllib3HttpConnection)

        # TODO - Compose a query for possibly multiple archives
        # TODO - Compose a query for the last day's papers from the specified archive
        q = Q("match_all")

        # TODO - Add all requested categories to the eprints struct

        # Perform the search and create an EPrint object for every hit that is found
        response = Search(index='arxiv').using(es).query(q).execute()
        for hit in response:
            # Collect top-level properties from the hit
            archive = hit["primary_classification"]["archive"]
            arxiv_id = archive["id"]
            archive_name = archive["name"]
            paper_id = hit['paper_id']
            title = hit['title']
            abstract = hit['abstract']
            submitted_date = hit['submitted_date']
            updated_date = hit['updated_date']
            comments = hit['comments']
            journal_ref = hit['journal_ref']
            doi = hit['doi']

            # Copy the hit data for authors into the EPrint
            authors = list()
            for hit_author in hit['authors']:
                last_name = hit_author['last_name']
                full_name = hit_author['full_name']
                initials = hit_author['initials']
                author = Author(last_name, full_name, initials)
                authors.append(author)

            # Copy the hit data for categories into the EPrint
            category = hit['primary_classification'].to_dict()['category']
            primary_category = Category(category['name'], category['id'])
            secondary_categories = list()
            for classification in hit['secondary_classification']:
                category = classification['category'].to_dict()
                secondary_category = Category(category['name'], category['id'])
                secondary_categories.append(secondary_category)

            # Create the EPrint and add it to the collection to be returned
            eprint = EPrint(arxiv_id, archive_name, paper_id, title, abstract,
                            submitted_date, updated_date, comments, journal_ref, doi,
                            authors, primary_category, secondary_categories)
            eprints.append(eprint)

    except ElasticsearchException as e:
        pass

    return EPrintSet(request_categories, eprints)
