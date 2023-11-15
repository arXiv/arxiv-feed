"""Application factory for rss app."""
import os

from flask import Flask
from werkzeug.utils import import_string

from arxiv.base import Base

from feed import routes
from feed.cache import cache

from flask_sqlalchemy import SQLAlchemy
from feed.tables import metadata

db=SQLAlchemy(metadata=metadata)

def create_web_app() -> Flask:
    """Initialize and configure the rss application."""
    app = Flask("feed")
    if "PYTEST_CURRENT_TEST" in os.environ:
        configuration = "testing"
    else:
        configuration = os.environ.get("ARXIV_FEED_CONFIGURATION", "production")
    app.config.from_object(
        import_string(f"feed.config.{configuration.title()}")()
    )
    Base(app)
    app.register_blueprint(routes.blueprint)
    cache.init_app(app)

    db.init_app(app)
    return app
