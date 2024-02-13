"""Flask configuration."""

import os
from feed import consts
from zoneinfo import ZoneInfo


class Config:
    """Base configuration object."""

    DEBUG = False
    TESTING = False
    VERSION = "1.1"

    BASE_SERVER = os.environ.get("BASE_SERVER", "arxiv.org")
    RSS_SERVER = os.environ.get("RSS_SERVER", "rss.arxiv.org")
    INFO_SERVER = os.environ.get("INFO_SERVER", "info.arxiv.org")
    STATIC_SERVER = os.environ.get("STATIC_SERVER", "static.arxiv.org")

    FEED_NUM_DAYS = os.environ.get("FEED_NUM_DAYS", consts.FEED_NUM_DAYS)

    ARXIV_BUSINESS_TZ = ZoneInfo(os.environ.get('ARXIV_BUSINESS_TZ', 'America/New_York'))

    URLS =[
        ("pdf", "/pdf/<arxiv:paper_id>v<string:version>", BASE_SERVER),
        ("pdf_by_id", "/pdf/<arxiv:paper_id>", BASE_SERVER),
        ("taxonomy", "/category_taxonomy", BASE_SERVER),
        ("rss", "/rss", RSS_SERVER),
        ("atom", "/atom", RSS_SERVER),
        ("help","/help/rss.html", INFO_SERVER),
        ("static","/static/<path:file_path>", STATIC_SERVER)
    ]

    ### database connection
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///tests/data/test_data.db')
    CLASSIC_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO: bool = os.environ.get("SQLALCHEMY_ECHO", "False")=="True"


class Production(Config):
    """Production configuration."""

    BASE_SERVER = "arxiv.org"


class Beta(Config):
    """Beta environment configuration."""

    BASE_SERVER = "beta.arxiv.org"


class Development(Config):
    """Development configuration."""

    DEBUG = True

    BASE_SERVER = "127.0.0.1"

    FEED_NUM_DAYS = 1 #set to a large number if you want more than one days entries


class Testing(Config):
    """Configuration for running tests."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///tests/data/test_data.db'
    CLASSIC_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
