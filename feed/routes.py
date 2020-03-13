"""URL routes for RSS feeds."""
from typing import Union

from werkzeug import Response
from werkzeug.exceptions import BadRequest
from flask import request, Blueprint, make_response

from feed import controller
from feed.errors import FeedError
from feed.consts import FeedVersion


blueprint = Blueprint("rss", __name__, url_prefix="/")


def _feed(arxiv_id: str, version: Union[str, FeedVersion]) -> Response:
    """Return the feed in appropriate format for the past day.

    Parameters
    ----------
    arxiv_id : str
        The ID code for the archive that is being searched.

    Returns
    -------
    response: Response
        Flask response object populated with the RSS or ATOM (XML) response for
        the request and ETag header added.
    """
    try:
        version = FeedVersion.get(version)
        feed = controller.get_feed(arxiv_id, version)
    except FeedError as ex:
        raise BadRequest(ex.error)

    # Create response object from data
    response: Response = make_response(feed.content)
    # Set headers
    response.headers["ETag"] = feed.etag
    response.headers["Content-Type"] = feed.content_type

    return response


@blueprint.route("/rss/<string:arxiv_id>", methods=["GET"])
def rss(arxiv_id: str) -> Response:
    """Return the RSS 2.0 results for the past day."""
    return _feed(arxiv_id=arxiv_id, version=FeedVersion.RSS_2_0)


@blueprint.route("/atom/<string:arxiv_id>", methods=["GET"])
def atom(arxiv_id: str) -> Response:
    """Return the Atom 1.0 results for the past day."""
    return _feed(arxiv_id=arxiv_id, version=FeedVersion.ATOM_1_0)


@blueprint.route("/<string:arxiv_id>", methods=["GET"])
def default(arxiv_id: str) -> Response:
    """Return RSS 2.0 results for the past day."""
    return _feed(
        arxiv_id=arxiv_id,
        version=request.headers.get("VERSION", FeedVersion.RSS_2_0),
    )
