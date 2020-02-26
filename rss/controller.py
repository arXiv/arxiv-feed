"""Controller for RSS Feeds."""

from http import HTTPStatus
from datetime import datetime
from typing import Tuple, Optional, Any, cast

from pytz import UTC
from flask import current_app
from werkzeug.exceptions import BadRequest

from rss import index
from rss.index import RssIndexerError
from rss.serializers.rss_2_0 import RSS_2_0
from rss.serializers.atom_1_0 import Atom_1_0
from rss.serializers.serializer import Serializer


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
    date_time = datetime.now(UTC)

    # Get the number of days for which results are to be returned
    days = int(cast(str, current_app.config["RSS_NUM_DAYS"]))

    # Create the correct serializer
    if version in (VER_RSS_2_0, None):
        serializer = RSS_2_0()  # type: Serializer
    elif version == VER_ATOM_1_0:
        serializer = Atom_1_0()
    else:
        raise BadRequest(
            f"Unsupported RSS version '{version}' requested."
            f"Valid options are '{VER_RSS_2_0}' and '{VER_ATOM_1_0}'."
        )
    # Get the search results, pass them to the serializer, return the results
    try:
        documents = index.perform_search(archive_id, date_time, days)
        data = serializer.get_xml(documents)
    except RssIndexerError as ex:
        raise BadRequest(ex.message)

    # TODO - We may eventually want to return an etag in the header
    return data, HTTPStatus.OK, {}
