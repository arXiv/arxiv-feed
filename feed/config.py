"""Flask configuration."""

import os
from typing import List, Tuple

import arxiv.config as arxiv_base


from feed import consts

class Settings(arxiv_base.Settings):
    """Base configuration object."""

    DEBUG: bool = False
    TESTING: bool = False
    VERSION:str = "1.1"

    STATIC_SERVER:str = os.environ.get("STATIC_SERVER", "static.arxiv.org")

    FEED_NUM_DAYS:int = int(os.environ.get("FEED_NUM_DAYS", consts.FEED_NUM_DAYS))

    ###add to the default URLS
    URLS: List[Tuple[str, str, str]] = [
        ("static","/static/<path:file_path>", STATIC_SERVER)
    ]

    ### database connection handled by base
    SQLALCHEMY_TRACK_MODIFICATIONS:bool = False
    SQLALCHEMY_ECHO: bool = os.environ.get("SQLALCHEMY_ECHO", "False")=="True"

