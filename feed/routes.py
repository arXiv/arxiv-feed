"""URL routes for RSS feeds."""
from typing import Union
from datetime import timedelta

from werkzeug import Response
from flask import request, Blueprint, make_response, redirect, url_for, current_app

from arxiv.taxonomy.definitions import ARCHIVES_ACTIVE

from feed import controller
from feed.consts import FeedVersion
from feed.serializers.serializer import serialize
from feed.errors import FeedError, FeedVersionError
from feed.utils import get_arxiv_midnight, utc_now
from feed.database import check_service


blueprint = Blueprint("feed", __name__, url_prefix="/")

@blueprint.route("/feed/status")
def status() -> Response:
    text=f"Status: {check_service()} Version: {current_app.config['VERSION']}"
    return make_response(text, 200)


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
        feed = serialize(documents, query=query, version=version)
    except FeedVersionError as ex:
        feed = serialize(ex, query=query)
    except FeedError as ex:
        feed = serialize(ex, query=query, version=version)


    # Create response object from data
    response: Response = make_response(feed.content, feed.status_code)
    # Set headers
    response.headers["ETag"] = feed.etag
    response.headers["Content-Type"] = feed.content_type
    expiration_time = (get_arxiv_midnight() + timedelta(hours=24) - utc_now()).total_seconds() #expire on next day
    response.headers['Cache-Control'] = f"max-age={int(expiration_time)}"
    return response

@blueprint.route("/")
def feed_home()-> Response:
    """Returns a empty error page"""
    rss_url=url_for("feed.rss", query="", _external=True)
    atom_url=url_for("feed.atom", query="", _external=True)
    help_url=url_for("help")+"/rss.html"
    rss=f"<a href='{rss_url}'>{rss_url}[archive or category]</a>"
    atom=f"<a href='{atom_url}'>{atom_url}[archive or category]</a>"
    help=f"<a href='{help_url}'>here</a>"
    help_text=f"Please use {rss} for RSS 2.0 and {atom} for ATOM formats. See {help} for help."
    return make_response(help_text, 200)

@blueprint.route("/rss")
@blueprint.route("/atom")
def feed_help()-> Response:
    """Returns a empty error page"""
    archives=', '.join(key for key in ARCHIVES_ACTIVE.keys() if key != 'test')
    help=f"<a href='{url_for('home')}category_taxonomy'>here</a>"
    return make_response(f"No archive specified. Archives are: {archives}. See {help} to learn about ArXiv category taxonomy.", 200)

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

@blueprint.route("/favicon.ico")
@blueprint.route("/apple-touch-icon-120x120-precomposed.png")
@blueprint.route("/apple-touch-icon-120x120.png")
@blueprint.route("/apple-touch-icon-precomposed.png")
def favicon() -> Response:
    """Send favicon."""
    url=url_for("static", file_path="browse/0.3.4/images/icons/favicon.ico")
    return redirect(url,code=301)