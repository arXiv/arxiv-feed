import string
from zoneinfo import ZoneInfo
from datetime import timezone, datetime
from unittest.mock import patch

from feed.utils import utc_now, randomize_case, etag, get_arxiv_midnight

# utc_now
def test_utc_now_timezone():
    now = utc_now()
    assert now.tzinfo == timezone.utc


# randomize_case
def test_randomize_case_ascii():
    assert any(c.isupper() for c in randomize_case("all lowercase string"))
    assert any(c.islower() for c in randomize_case("ALL UPPERCASE STRING"))


def test_randomize_case_unicode():
    assert any(c.isupper() for c in randomize_case("само мала слова"))
    assert any(c.islower() for c in randomize_case("САМО ВЕЛИКА СЛОВА"))


def test_randomize_case_non_letters():
    assert string.digits == randomize_case(string.digits)
    assert string.punctuation == randomize_case(string.punctuation)
    assert string.whitespace == randomize_case(string.whitespace)


def test_randomize_case_edge_cases():
    assert "" == randomize_case("")


# etag

def test_etag():
    assert etag("content") == etag(b"content")
    assert etag("Садржај") == etag("Садржај".encode("utf-8"))
    assert etag("foo") != etag("bar")


@patch("feed.utils.datetime")
def test_get_arxiv_midnight(mock_datetime, app):
    mock_datetime.now.return_value = datetime(2023, 11, 10, 2, 30, 45, tzinfo=ZoneInfo('UTC'))
    with app.app_context():
        result = get_arxiv_midnight()

    assert result == datetime(2023, 11, 9, 0, 0, 0, tzinfo=ZoneInfo("America/New_York"))