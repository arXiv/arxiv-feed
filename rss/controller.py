"""Controller for RSS Feeds."""

import logging
import hashlib
from typing import Tuple
from flask import current_app

from rss import index
from rss import consts
from rss import serializers
from rss.consts import FeedVersion
from rss.errors import FeedVersionError
from rss.serializers.serializer import Serializer


logger = logging.getLogger(__name__)


def get_feed(archive_id: str, version: FeedVersion) -> Tuple[str, str]:
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
    data : str
        The serialized XML results of the search.
    etag: str
        Feed etag.

    Raises
    ------
    FeedError
        Either FeedVersionError if the feed version is incorrect or
        FeedIndexError if it fails to fetch the feed from ElasticSearch.
    """
    # Get the number of days for which results are to be returned
    feed_num_days = current_app.config.get(
        "FEED_NUM_DAYS", consts.FEED_NUM_DAYS
    )
    try:
        days = int(feed_num_days)
    except ValueError:
        logger.error(
            "Invalid configuration - FEED_NUM_DAYS: '%s'. Setting to 1.",
            feed_num_days,
        )
        days = 1

    # Create the correct serializer
    if version == FeedVersion.RSS_2_0:
        serializer: Serializer = serializers.RSS20()
    elif version == FeedVersion.ATOM_1_0:
        serializer: Serializer = serializers.Atom10()
    else:
        raise FeedVersionError(version)

    # Get the search results, pass them to the serializer, return the results
    documents = index.search(archive_id, days)
    data = serializer.get_feed(documents)
    etag = hashlib.sha256(data.encode("utf-8"))
    return data, etag.hexdigest()
