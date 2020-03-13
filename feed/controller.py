"""Controller for RSS Feeds."""

import logging
from flask import current_app

from feed import index
from feed.consts import FeedVersion
from feed.serializers.serializer import Serializer, Feed


logger = logging.getLogger(__name__)


def get_feed(archive_id: str, version: FeedVersion) -> Feed:
    """
    Return the past day's RSS content from the specified XML serializer.

    Parameters
    ----------
    archive_id : str
        An ID identifying the archive to search.
    version : str
        The RSS format/version to use when serializing the results.

    Returns
    -------
    Feed
        Feed object containing the serialized feed.

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
    documents = index.search(archive_id, days)
    serializer = Serializer(documents=documents, version=version)
    return serializer.serialize()
