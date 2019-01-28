"""URL routes for RSS feeds"""

from flask import Blueprint
from flask import request
from rss import controller

blueprint = Blueprint('rss', __name__, url_prefix='/rss')


@blueprint.route('/<string:archive_id>', methods=['GET', 'POST'])
def rss(archive_id: str) -> tuple:
    """
    Return RSS results for the past day in the format specified by URL parameters.

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

    version = request.args.get('version')
    data, status, headers = controller.get_xml(archive_id, version)
    # TODO: create a flask response object to hold the data?
    return data, status, headers
