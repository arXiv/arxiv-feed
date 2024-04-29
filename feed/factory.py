"""Application factory for rss app."""
import os
from flask import Flask

from arxiv.base import Base

from feed.config import Settings
from feed import routes

def create_web_app() -> Flask:
    """Initialize and configure the rss application."""
    settings = Settings()
    app = Flask("feed")
    app.config.from_object(settings)
    Base(app)
    app.url_map.strict_slashes = False
    app.register_blueprint(routes.blueprint)
    return app
