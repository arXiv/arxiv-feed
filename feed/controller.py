"""Controller for RSS Feeds."""

import logging
from flask import current_app

from feed import index
from feed.domain import DocumentSet


logger = logging.getLogger(__name__)


def get_documents(archive_id: str) -> DocumentSet:
    """
    Return the past day's RSS content from the specified XML serializer.

    Parameters
    ----------
    archive_id : str
        An ID identifying the archive to search.

    Returns
    -------
    DocumentSet
        DocumentSet object populated with search results.

    Raises
    ------
    FeedError
        Either FeedVersionError if the feed version is incorrect or
        FeedIndexError if it fails to fetch the feed from ElasticSearch.
    """
    # Get the number of days for which results are to be returned
    feed_num_days: str = current_app.config["FEED_NUM_DAYS"]
    try:
        days = int(feed_num_days)
    except ValueError:
        logger.error(
            "Invalid configuration - FEED_NUM_DAYS: '%s'. Setting to 1.",
            feed_num_days,
        )
        days = 1

    # Get the search results, pass them to the serializer, return the results
    return index.search(archive_id, days)
