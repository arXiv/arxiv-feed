"""URL routes for RSS feeds."""
from typing import Union

from werkzeug import Response
from flask import request, Blueprint, make_response

from feed import controller
from feed.cache import cache
from feed.utils import hash_query
from feed.consts import FeedVersion
from feed.serializers import serialize, Feed
from feed.errors import FeedError, FeedVersionError


blueprint = Blueprint("rss", __name__, url_prefix="/")


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
    # Calculate unique key for the query
    key = f"{hash_query(query)}-{version}"

    # Try to get feed from cache
    value = cache.get(key)

    if value is not None:
        try:
            feed = Feed.from_string(value)
        except ValueError as ex:
            feed = serialize(ex)
    else:
        # Cache failed to generate feed
        try:
            version = FeedVersion.get(version)
            documents = controller.get_documents(query)
            feed = serialize(documents, version=version)
        except FeedVersionError as ex:
            feed = serialize(ex)
        except FeedError as ex:
            feed = serialize(ex, version=version)
        # Save feed to cache
        cache.set(key, feed.to_string())

    # Create response object from data
    response: Response = make_response(feed.content, feed.status_code)
    # Set headers
    response.headers["ETag"] = feed.etag
    response.headers["Content-Type"] = feed.content_type
    return response


@blueprint.route("/rss/<string:query>", methods=["GET"])
def rss(query: str) -> Response:
    """Return the RSS 2.0 results for the past day."""
    return _feed(query=query, version=FeedVersion.RSS_2_0)


@blueprint.route("/atom/<string:query>", methods=["GET"])
def atom(query: str) -> Response:
    """Return the Atom 1.0 results for the past day."""
    return _feed(query=query, version=FeedVersion.ATOM_1_0)


@blueprint.route("/<string:query>", methods=["GET"])
def default(query: str) -> Response:
    """Return RSS 2.0 results for the past day."""
    return _feed(
        query=query,
        version=request.headers.get("VERSION", FeedVersion.RSS_2_0),
    )
