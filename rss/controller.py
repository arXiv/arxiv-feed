"""Controller for RSS Feeds."""

from typing import Tuple, Optional, Any
from pytz import UTC
from arxiv import status
from rss import index
from rss.serializers.serializer import Serializer
from rss.serializers.rss_2_0 import RSS_2_0
from rss.serializers.atom_1_0 import Atom_1_0

import datetime

VER_RSS_2_0 = "2.0"
VER_ATOM_1_0 = "atom_1.0"


def get_xml(archive_id: str, version: Optional[Any]) -> Tuple[str, int, dict]:
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
    status_code
        The status code for the operation.
    header
        HTML headers for the response to the request.

    """
    # Get the current date and time
    date_time = datetime.datetime.now(UTC)

    # Create the correct serializer
    if version in (VER_RSS_2_0, None):
        serializer = RSS_2_0()  # type: Serializer
    elif version == VER_ATOM_1_0:
        serializer = Atom_1_0()
    else:
        return "", status.HTTP_400_BAD_REQUEST, {}

    # Get the search results, pass them to the serializer, return the results
    hits = index.perform_search(archive_id, date_time)
    data, status_code = serializer.get_xml(hits)

    # TODO - We may eventually want to return an etag in the header
    return data, status_code, {}
