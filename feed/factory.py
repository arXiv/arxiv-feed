"""Application factory for rss app."""
import os

from flask import Flask
from werkzeug.utils import import_string

from feed import routes


def create_web_app() -> Flask:
    """Initialize and configure the rss application."""
    app = Flask("rss")
    configuration = os.environ.get("ARXIV_FEED_CONFIGURATION", "production")
    app.config.from_object(
        import_string(f"feed.config.{configuration.title()}")()
    )
    app.register_blueprint(routes.blueprint)

    return app
