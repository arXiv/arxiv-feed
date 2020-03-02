"""Flask configuration."""

import os

VERSION = "0.3"

BASE_SERVER = os.environ.get("BASE_SERVER", "arxiv.org")

METADATA_ENDPOINT = os.environ.get(
    "METADATA_ENDPOINT", "https://beta.arxiv.org/"
)

FEED_NUM_DAYS = os.environ.get("FEED_NUM_DAYS", "1")

URLS = [
    ("pdf", "/pdf/<arxiv:paper_id>v<string:version>", BASE_SERVER),
    ("abs", "/abs/<arxiv:paper_id>v<string:version>", BASE_SERVER),
    ("abs_by_id", "/abs/<arxiv:paper_id>", BASE_SERVER),
    ("pdf_by_id", "/pdf/<arxiv:paper_id>", BASE_SERVER),
    ("pdfonly", "/pdf/<arxiv:paper_id>v<string:version>", BASE_SERVER),
]
