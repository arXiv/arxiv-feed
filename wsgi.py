"""Web Server Gateway Interface (WSGI) entry-point."""
import os

from feed.factory import create_web_app

# We need someplace to keep the flask app around between requests.
# Double underscores excludes this from * imports.
__flask_app__ = None


def application(environ, start_response):
    """WSGI application, called once for each HTTP request."""
    # Copy string WSGI envrion to os.environ. This is to get apache
    # SetEnv vars.  It needs to be done before the call to
    # create_web_app() due to how config is setup from os in
    # browse/config.py.
    for key, value in environ.items():
        if type(value) is str:
            os.environ[key] = value

    # 'global' actually means module scope, and that is exactly what
    # we want here.
    global __flask_app__
    if __flask_app__ is None:
        __flask_app__ = create_web_app()

    return __flask_app__(environ, start_response)
