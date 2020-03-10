import pytest

from feed.consts import FeedVersion
from feed.utils import randomize_case
from feed.errors import FeedVersionError


# FeedVersion.supported


def test_feed_version_supported():
    assert FeedVersion.supported() == {
        FeedVersion.RSS_2_0,
        FeedVersion.ATOM_1_0,
    }


# FeedVersion.get


def test_feed_version_get_supported():
    # RSS full version
    assert (
        FeedVersion.get(randomize_case(FeedVersion.RSS_2_0.lower()))
        == FeedVersion.RSS_2_0
    )
    # RSS only number
    assert FeedVersion.get("2.0") == FeedVersion.RSS_2_0

    # Atom full version
    assert (
        FeedVersion.get(randomize_case(FeedVersion.ATOM_1_0.lower()))
        == FeedVersion.ATOM_1_0
    )
    # Atom only number
    assert FeedVersion.get("1.0", atom=True) == FeedVersion.ATOM_1_0


def test_feed_version_get_unsupported():
    # RSS 0.91 full version
    rss_0_91 = randomize_case(FeedVersion.RSS_0_91)
    with pytest.raises(FeedVersionError) as excinfo:
        FeedVersion.get(rss_0_91)

    ex: FeedVersionError = excinfo.value
    assert ex.version == rss_0_91
    assert ex.supported == FeedVersion.supported()

    # RSS 0.91 only number
    with pytest.raises(FeedVersionError) as excinfo:
        FeedVersion.get("0.91")

    ex: FeedVersionError = excinfo.value
    assert ex.version == "RSS 0.91"
    assert ex.supported == FeedVersion.supported()

    # RSS 1.0 full version
    rss_1_0 = randomize_case(FeedVersion.RSS_1_0)
    with pytest.raises(FeedVersionError) as excinfo:
        FeedVersion.get(rss_1_0)

    ex: FeedVersionError = excinfo.value
    assert ex.version == rss_1_0
    assert ex.supported == FeedVersion.supported()

    # RSS 1.0 only number
    with pytest.raises(FeedVersionError) as excinfo:
        FeedVersion.get("1.0")

    ex: FeedVersionError = excinfo.value
    assert ex.version == "RSS 1.0"
    assert ex.supported == FeedVersion.supported()


def test_feed_version_get_invalid():
    # RSS
    for version, test in [
        ("RSS 3.3", "3.3"),
        ("RSS 0.1", "0.1"),
        ("RSS 1.1", "RSS 1.1"),
        ("RSS 2.1", "RSS 2.1"),
    ]:
        with pytest.raises(FeedVersionError) as excinfo:
            FeedVersion.get(test)

        ex: FeedVersionError = excinfo.value
        assert ex.version == version
        assert ex.supported == FeedVersion.supported()

    # Atom
    for version, test, prefere in [
        ("Atom 0.1", "0.1", True),
        ("Atom 0.91", "0.91", True),
        ("Atom 2.0", "2.0", True),
        ("Atom 0.1", "Atom 0.1", False),
        ("Atom 0.91", "Atom 0.91", False),
        ("Atom 2.0", "Atom 2.0", False),
    ]:
        with pytest.raises(FeedVersionError) as excinfo:
            FeedVersion.get(test, atom=prefere)

        ex: FeedVersionError = excinfo.value
        assert ex.version == version
        assert ex.supported == FeedVersion.supported()

    # Nonsense
    for version in ["foo", "bar", "baz"]:
        with pytest.raises(FeedVersionError) as excinfo:
            FeedVersion.get(version)

        ex: FeedVersionError = excinfo.value
        assert ex.version == version
        assert ex.supported == FeedVersion.supported()
