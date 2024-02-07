"""Application factory for rss app."""
import os

from flask import Flask
from werkzeug.utils import import_string

from arxiv.base import Base

from feed import routes

from flask_sqlalchemy import SQLAlchemy
from feed.tables import db

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
    app.url_map.strict_slashes = False
    app.register_blueprint(routes.blueprint)

    db.init_app(app)
    return app
