from datetime import datetime, timezone


def utc_now() -> datetime:
    """Return the current timestamp localized to UTC."""
    return datetime.now().astimezone(timezone.utc)
