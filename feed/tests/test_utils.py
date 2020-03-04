from datetime import timezone

from feed.utils import utc_now


def test_utc_now_timezone():
    now = utc_now()
    assert now.tzinfo == timezone.utc
