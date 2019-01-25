"""URL routes for RSS feeds"""

from flask.json import jsonify
from flask import Blueprint
from werkzeug.exceptions import NotFound
from arxiv import status

blueprint = Blueprint('rss', __name__, url_prefix='')


@blueprint.route('/rss', methods=['GET', 'POST'])
def rss() -> tuple:
    """
    Return RSS results for the past day in the format specified by URL parameters.

    TODO - Determine output classification and version from URL parameters
    TODO - Invoke controller with those parameters

    Returns
    -------
    tuple
        content and status

    """
    return jsonify({'results': 'TBD'}), status.HTTP_200_OK
