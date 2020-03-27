import re
import random
import hashlib
from typing import Union
from datetime import datetime, timezone

from feed.consts import DELIMITER


# Get a random seed
random.seed()


def utc_now() -> datetime:
    """Return the current timestamp localized to UTC."""
    return datetime.now().astimezone(timezone.utc)


# Used only in tests

UNICODE_LETTERS_RE = re.compile(r"[^\W\d_]", re.UNICODE)


def randomize_case(s: str) -> str:
    """Randomize string casing.

    Parameters
    ----------
    s : str
        Original string

    Returns
    -------
    str
        String with it's letters in randomized casing.
    """
    result = "".join(
        [c.upper() if random.randint(0, 1) == 1 else c.lower() for c in s]
    )

    # If result contains letters and the result is same as original try again.
    if UNICODE_LETTERS_RE.search(s) is not None and result == s:
        return randomize_case(s)
    else:
        return result


def hash_query(query: str) -> str:
    """Return a hash of query that is not dependent on the query order."""
    parts = [part.strip() for part in query.split(DELIMITER)]
    parts.sort()
    return hashlib.sha256(DELIMITER.join(parts).encode("utf-8")).hexdigest()


def etag(content: Union[str, bytes]) -> str:
    """Calculate a unique ETag for the provided content.

    Parameters
    ----------
    content : Union[str, bytes]
        Content for which the etag should be calculated.

    Returns
    -------
    str
        Calculated etag.
    """
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest()
