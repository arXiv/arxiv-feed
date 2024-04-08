"""Flask configuration."""

import os
from typing import List, Tuple

import arxiv.config as arxiv_base


from feed import consts

class Settings(arxiv_base.Settings):
    """Base configuration object."""

    DEBUG = False
    TESTING = False
    VERSION = "1.1"

    BASE_SERVER = os.environ.get("BASE_SERVER", "arxiv.org")
    RSS_SERVER = os.environ.get("RSS_SERVER", "rss.arxiv.org")
    STATIC_SERVER = os.environ.get("STATIC_SERVER", "static.arxiv.org")

    FEED_NUM_DAYS = os.environ.get("FEED_NUM_DAYS", consts.FEED_NUM_DAYS)

    ###add to the 
    URLS: List[Tuple[str, str, str]] = [
        ("taxonomy", "/category_taxonomy", BASE_SERVER),
        ("static","/static/<path:file_path>", STATIC_SERVER)
    ]

    ### database connection handled by base
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO: bool = os.environ.get("SQLALCHEMY_ECHO", "False")=="True"

