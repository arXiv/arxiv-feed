"""Controller for RSS Feeds."""

import logging
from flask import current_app

from feed import fetch_data
from feed.domain import DocumentSet


logger = logging.getLogger(__name__)


def get_documents(query: str) -> DocumentSet:
    """
    Return the past day's RSS content from the specified XML serializer.

    Parameters
    ----------
    query : str
        A concatenation of archive/category specifiers separated by delimiter
        characters.

    Returns
    -------
    DocumentSet
        DocumentSet object populated with search results.

    Raises
    ------
    FeedError
        Either FeedVersionError if the feed version is incorrect or
        FeedIndexError if it fails to fetch the feed.
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
    return fetch_data.search(query, days)
