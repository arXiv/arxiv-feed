"""Interface to Index Service for RSS feeds."""

from elasticsearch import Elasticsearch, ElasticsearchException
from elasticsearch.connection import Urllib3HttpConnection
from elasticsearch_dsl import Search, Q
import datetime
from typing import List


def perform_search(archive: str, date_time: datetime.datetime) -> List:
    """
    Search the index for records with the archive ID and dated within 24 hours of date_time.

    Parameters
    ----------
    archive : str
        The ID of the archive to search
    date_time : datetime
        The date/time that defines the end of the 24 hour search window.

    Returns
    -------
    hits : List
        The results of the Elasticsearch search as a list of .

    """
    hits = []
    try:
        es = Elasticsearch([{'host': 'localhost', 'port': 9200,
                             'use_ssl': False,
                             'http_auth': None,
                             'verify_certs': True}],
                           connection_class=Urllib3HttpConnection)

        # TODO - Compose a query for the last day's papers from the specified archive
        q = Q("match_all")

        response = Search(index='arxiv').using(es).query(q).execute()
        for hit in response:
            hits.append(hit)

    except ElasticsearchException as e:
        pass

    return hits
