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

    URLS = {
        "pdf": f"https://{BASE_SERVER}/pdf/{{paper_id}}v{{version}}",
        "abs": f"https://{BASE_SERVER}/abs/{{paper_id}}v{{version}}",
        "abs_by_id": f"https://{BASE_SERVER}/abs/{{paper_id}}",
        "pdf_by_id": f"https://{BASE_SERVER}/pdf/{{paper_id}}",
        "ps_by_id": f"https://{BASE_SERVER}/ps/{{paper_id}}",
        "pdf_only": f"https://{BASE_SERVER}/pdf/{{paper_id}}v{{version}}",
    }

    # Cache
    CACHE_TYPE = "redis"
    CACHE_DEFAULT_TIMEOUT = int(
        os.environ.get("CACHE_DEFAULT_TIMEOUT", "86400")
    )  # 1 day
    CACHE_REDIS_HOST = os.environ.get("CACHE_REDIS_HOST", "127.0.0.1")
    CACHE_REDIS_PORT = int(os.environ.get("CACHE_REDIS_PORT", "6379"))
    CACHE_REDIS_DB = int(os.environ.get("CACHE_REDIS_DB", "0"))

    # ElasticSearch
    ELASTICSEARCH_HOST = os.environ.get("ELASTICSEARCH_HOST", "127.0.0.1")
    ELASTICSEARCH_PORT = int(os.environ.get("ELASTICSEARCH_PORT", "9200"))
    ELASTICSEARCH_SSL = (
        os.environ.get("ELASTICSEARCH_SSL", "false").lower() == "true"
    )
    ELASTICSEARCH_INDEX = os.environ.get("ELASTICSEARCH_INDEX", "arxiv")

    ### atempting to connect to database
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    CLASSIC_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False


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

    FEED_NUM_DAYS = 100000


class Testing(Config):
    """Configuration for running tests."""

    TESTING = True

    CACHE_TYPE = "null"
