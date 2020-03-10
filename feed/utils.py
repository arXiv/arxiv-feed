import re
import random
from datetime import datetime, timezone


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
