"""URL routes for RSS feeds."""

from werkzeug import Response
from werkzeug.exceptions import BadRequest
from flask import Blueprint, request, make_response

from feed import controller
from feed.errors import FeedError
from feed.consts import FeedVersion

blueprint = Blueprint("rss", __name__, url_prefix="/rss")


# FIXME: I would change this in the following way:
#        Root url / is predefined atom or rss 2.0 (I have no preference), and
#        hen have separate urls (/rss.xml and /atom.xml) if the user wants to
#        pick a different feed format.


@blueprint.route("/<string:archive_id>", methods=["GET"])
def rss(archive_id: str) -> Response:
    """Return RSS results for the past day.

    Format is specified by URL parameters.

    Parameters
    ----------
    archive_id : str
        The ID code for the archive that is being searched.

    Returns
    -------
    data : str
        The RSS (XML) response for the request.
    status
        The outcome status for the request.
    headers
        Headers associated with the response.

    """
    version = request.args.get("version", FeedVersion.RSS_2_0)
    try:
        data, etag = controller.get_feed(archive_id, version)
    except FeedError as ex:
        raise BadRequest(ex.error)

    response: Response = make_response(data)
    response.headers["ETag"] = etag
    return response
