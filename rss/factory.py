"""Application factory for rss app."""


from flask import Flask

# from arxiv.base import logging

from rss import routes
# from rss.services import baz
# from rss.encode import ISO8601JSONEncoder
# from rss.middleware import auth
# from arxiv.base.middleware import wrap
from arxiv.base import Base


def create_web_app() -> Flask:
    """Initialize and configure the rss application."""
    app = Flask('rss')
    app.config.from_pyfile('config.py')
    # app.json_encoder = ISO8601JSONEncoder

    # baz.init_app(app)

    Base(app)    # Gives us access to the base UI templates and resources.
    app.register_blueprint(routes.blueprint)

    # wrap(app, [auth.ExampleAuthMiddleware])

    return app
