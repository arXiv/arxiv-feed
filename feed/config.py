"""Flask configuration."""

import os
from feed import consts


class Config(object):
    DEBUG = False
    TESTING = False
    VERSION = "0.3"
    BASE_SERVER = os.environ.get("BASE_SERVER", "arxiv.org")

    METADATA_ENDPOINT = os.environ.get(
        "METADATA_ENDPOINT", f"https://{BASE_SERVER}"
    )

    FEED_NUM_DAYS = os.environ.get("FEED_NUM_DAYS", consts.FEED_NUM_DAYS)

    URLS = {
        "pdf": f"https://{BASE_SERVER}/pdf/{{paper_id}}v{{version}}",
        "abs": f"https://{BASE_SERVER}/abs/{{paper_id}}v{{version}}",
        "abs_by_id": f"https://{BASE_SERVER}/abs/{{paper_id}}",
        "pdf_by_id": f"https://{BASE_SERVER}/pdf/{{paper_id}}",
        "pdf_only": f"https://{BASE_SERVER}/pdf/{{paper_id}}v{{version}}",
    }


class Production(Config):
    BASE_SERVER = "arxiv.org"
    METADATA_ENDPOINT = f"https://{BASE_SERVER}"


class Beta(Config):
    BASE_SERVER = "beta.arxiv.org"
    METADATA_ENDPOINT = f"https://{BASE_SERVER}"


class Development(Config):
    DEBUG = True

    BASE_SERVER = "127.0.0.1"
    METADATA_ENDPOINT = f"https://beta.arxiv.org"

    FEED_NUM_DAYS = 100000


class Testing(Config):
    TESTING = True
