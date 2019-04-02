"""Application factory for rss app."""


from flask import Flask
from arxiv.base import Base
from rss import routes


def create_web_app() -> Flask:
    """Initialize and configure the rss application."""
    app = Flask('rss')
    app.config.from_pyfile('config.py') # type: ignore

    Base(app)    # Gives us access to the base UI templates and resources.
    app.register_blueprint(routes.blueprint)

    return app
