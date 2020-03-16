"""URL routes for RSS feeds."""
from typing import Union

from werkzeug import Response
from flask import request, Blueprint, make_response

from feed import controller
from feed.consts import FeedVersion
from feed.serializers import serialize
from feed.errors import FeedError, FeedVersionError


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
        documents = controller.get_documents(arxiv_id)
        feed = serialize(documents, version=version)
    except FeedVersionError as ex:
        feed = serialize(ex)
    except FeedError as ex:
        feed = serialize(ex, version=version)

    # Create response object from data
    response: Response = make_response(feed.content, feed.status_code)
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
