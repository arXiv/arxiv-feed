import string
from datetime import timezone

from feed.utils import utc_now, randomize_case

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
