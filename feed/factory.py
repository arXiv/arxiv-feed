"""Application factory for rss app."""

from flask import Flask

from feed import routes


def create_web_app() -> Flask:
    """Initialize and configure the rss application."""
    app = Flask("rss")
    app.config.from_pyfile("config.py")
    app.register_blueprint(routes.blueprint)

    return app
