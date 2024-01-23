"""URL routes for RSS feeds."""
from typing import Union

from werkzeug import Response
from flask import request, Blueprint, make_response

from feed import controller
from datetime import datetime, timedelta

from feed.consts import FeedVersion
from feed.serializers import serialize
from feed.errors import FeedError, FeedVersionError
from feed.utils import get_arxiv_midnight, utc_now


blueprint = Blueprint("rss", __name__, url_prefix="/")

@blueprint.route("/feed/status")
def status() -> Response:
    return make_response("good", 200)


def _feed(query: str, version: Union[str, FeedVersion]) -> Response:
    """Return the feed in appropriate format for the past day.

    Parameters
    ----------
    query : str
        A concatenation of archive/category specifiers separated by delimiter
        characters.

    Returns
    -------
    response: Response
        Flask response object populated with the RSS or ATOM (XML) response for
        the request and ETag header added.
    """
    try:
        version = FeedVersion.get(version)
        documents = controller.get_documents(query)
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
    expiration_time = (get_arxiv_midnight() + timedelta(hours=24) - utc_now()).total_seconds() #expire on next day
    response.headers['Cache-Control'] = f"max-age={int(expiration_time)}"
    return response


@blueprint.route("/rss")
@blueprint.route("/atom")
def feed_help()-> Response:
    """Returns a empty error page"""
    return make_response("No archive specified.", 200)


@blueprint.route("/rss/<string:query>", methods=["GET"])
def rss(query: str) -> Response:
    """Return the RSS results for the past day.

    Defaults to RSS 2.0 and only supports 2.0. 0.91 and 1.0 will raise errors."""
    return _feed(query=query,
                 version=request.args.get("version", default="2.0", type=str))


@blueprint.route("/atom/<string:query>", methods=["GET"])
def atom(query: str) -> Response:
    """Return the Atom 1.0 results for the past day."""
    return _feed(query=query, version=FeedVersion.ATOM_1_0)
