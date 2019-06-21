"""Controller for RSS Feeds."""

from typing import Tuple, Optional, Any, cast
from flask import current_app
from pytz import UTC
from arxiv import status
from rss import index
from rss.index import RssIndexerError
from rss.serializers.serializer import Serializer
from rss.serializers.rss_2_0 import RSS_2_0
from rss.serializers.atom_1_0 import Atom_1_0
from werkzeug.exceptions import BadRequest

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

    # Get the number of days for which results are to be returned
    days = int(cast(str, current_app.config['RSS_NUM_DAYS']))

    # Create the correct serializer
    if version in (VER_RSS_2_0, None):
        serializer = RSS_2_0()  # type: Serializer
    elif version == VER_ATOM_1_0:
        serializer = Atom_1_0()
    else:
        msg = "Unsupported RSS version '" + str(version) + "' requested." + \
              "Valid options are '" + VER_RSS_2_0 + "' and '" + VER_ATOM_1_0 + "'."
        raise BadRequest(msg)

    # Get the search results, pass them to the serializer, return the results
    try:
        eprints = index.perform_search(archive_id, date_time, days)
        data = serializer.get_xml(eprints)
    except RssIndexerError as e:
        raise BadRequest(e.message)

    # TODO - We may eventually want to return an etag in the header
    return data, status.HTTP_200_OK, {}
