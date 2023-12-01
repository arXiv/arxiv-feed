"""Flask configuration."""

import os
from feed import consts
from zoneinfo import ZoneInfo


class Config:
    """Base configuration object."""

    DEBUG = False
    TESTING = False
    VERSION = "0.3"
    BASE_SERVER = os.environ.get("BASE_SERVER", "arxiv.org")

    METADATA_ENDPOINT = os.environ.get(
        "METADATA_ENDPOINT", f"https://{BASE_SERVER}"
    )

    FEED_NUM_DAYS = os.environ.get("FEED_NUM_DAYS", consts.FEED_NUM_DAYS)

    ARXIV_BUSINESS_TZ = ZoneInfo(os.environ.get('ARXIV_BUSINESS_TZ', 'America/New_York'))

    URLS =[
        ("pdf", "/pdf/<arxiv:paper_id>v<string:version>", BASE_SERVER),
        ("pdf_by_id", "/pdf/<arxiv:paper_id>", BASE_SERVER),
        ("rss", "/rss/", BASE_SERVER),
        ("atom", "/atom/", BASE_SERVER)
    ]

    # Cache
    CACHE_TYPE = "null"
    CACHE_DEFAULT_TIMEOUT = int(
        os.environ.get("CACHE_DEFAULT_TIMEOUT", "86400")
    )  # 1 day
    CACHE_REDIS_HOST = os.environ.get("CACHE_REDIS_HOST", "127.0.0.1")
    CACHE_REDIS_PORT = int(os.environ.get("CACHE_REDIS_PORT", "6379"))
    CACHE_REDIS_DB = int(os.environ.get("CACHE_REDIS_DB", "0"))


    ### database connection
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    CLASSIC_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO: bool = os.environ.get("SQLALCHEMY_ECHO", "False")=="True"


class Production(Config):
    """Production configuration."""

    BASE_SERVER = "arxiv.org"
    METADATA_ENDPOINT = f"https://{BASE_SERVER}"


class Beta(Config):
    """Beta environment configuration."""

    BASE_SERVER = "beta.arxiv.org"
    METADATA_ENDPOINT = f"https://{BASE_SERVER}"


class Development(Config):
    """Development configuration."""

    DEBUG = True

    BASE_SERVER = "127.0.0.1"
    METADATA_ENDPOINT = f"https://beta.arxiv.org"

    FEED_NUM_DAYS = 1 #set to a large number if you want more than one days entries


class Testing(Config):
    """Configuration for running tests."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///tests/data/test_data.db'
    CLASSIC_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TYPE = "null"
