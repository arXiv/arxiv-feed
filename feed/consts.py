from enum import Enum
from typing import Set

from feed.errors import FeedVersionError


FEED_NUM_DAYS = 1

DELIMITER = "+"


class FeedVersion(str, Enum):
    RSS_0_91 = "RSS 0.91"
    RSS_1_0 = "RSS 1.0"
    RSS_2_0 = "RSS 2.0"
    ATOM_1_0 = "Atom 1.0"

    @property
    def is_rss(self) -> bool:
        """Return True if this is an RSS specification."""
        return self in (self.RSS_0_91, self.RSS_1_0, self.RSS_2_0)

    @property
    def is_atom(self) -> bool:
        """Return True if this is an Atom specification."""
        return self in (self.ATOM_1_0,)

    @classmethod
    def supported(cls) -> Set["FeedVersion"]:
        """Return a set of supported feed versions."""
        return {cls.RSS_2_0, cls.ATOM_1_0}

    @classmethod
    def get(cls, version: str, atom: bool = False) -> "FeedVersion":
        """Get feed version from its string representation.

        Parameters
        ----------
        version : str
            String representation of the feed version.
        atom : bool
            Should we prefer atom feed if the version is only a number.

        Returns
        -------
        FeedVersion
            Enum representation of the feed version.

        Raises
        ------
        FeedVersionError
            If the feed version is not supported.
        """
        version = version.strip()

        # Check if the version is only a number
        try:
            float(version)
            version = f"Atom {version}" if atom else f"RSS {version}"
        except ValueError:
            # It's a full version string, do nothing
            pass

        if version.lower() not in {v.lower() for v in cls.supported()}:
            raise FeedVersionError(version=version, supported=cls.supported())

        for fv in cls.supported():
            if fv.value.lower() == version.lower():
                return fv
        else:
            raise FeedVersionError(version=version, supported=cls.supported())
