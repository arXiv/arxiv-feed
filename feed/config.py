"""Flask configuration."""

import os
from feed import consts

VERSION = "0.3"

BASE_SERVER = os.environ.get("BASE_SERVER", consts.BASE_SERVER)

METADATA_ENDPOINT = os.environ.get(
    "METADATA_ENDPOINT", consts.METADATA_ENDPOINT
)

FEED_NUM_DAYS = os.environ.get("FEED_NUM_DAYS", consts.FEED_NUM_DAYS)

URLS = {
    "pdf": f"https://{BASE_SERVER}/pdf/{{paper_id}}v{{version}}",
    "abs": f"https://{BASE_SERVER}/abs/{{paper_id}}v{{version}}",
    "abs_by_id": f"https://{BASE_SERVER}/abs/{{paper_id}}",
    "pdf_by_id": f"https://{BASE_SERVER}/pdf/{{paper_id}}",
    "pdf_only": f"https://{BASE_SERVER}/pdf/{{paper_id}}v{{version}}",
}


