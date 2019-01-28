"""Controller for RSS Feeds"""

from typing import Tuple, Optional
import datetime
from arxiv import status
from rss import index
from rss.serializers.rss_2_0 import Rss_2_0
from rss.serializers.atom_1_0 import Atom_1_0


def get_xml(archive_id: str, version: str) -> Tuple[Optional[dict], int, dict]:
    """
    Returns the past day's RSS content from the specified XML serializer.

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
    date_time = datetime.datetime.now()

    # Create the correct serializer
    if version == "2.0":
        serializer = Rss_2_0()
    elif version == "atom_1.0":
        serializer = Atom_1_0()
    else:
        return None, status.HTTP_400_BAD_REQUEST, {}

    # Get the search results, pass them to the serializer, return the results
    response = index.perform_search(archive_id, date_time)
    data, status_code = serializer.get_xml(response)

    # TODO - temporary, for debugging
    print(data)

    # TODO - We may eventually want to return an etag in the header
    return data, status_code, {}
