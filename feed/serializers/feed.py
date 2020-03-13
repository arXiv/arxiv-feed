from typing import Optional

from feed import utils
from feed.consts import FeedVersion
from feed.errors import FeedVersionError


class Feed:
    """Representation of a feed.

    Parameters
    ----------
    content : str
        Feed xml content.
    version : FeedVersion
        Version of the feed specification.

    Raises
    ------
    FeedVersionError
        For invalid feed versions.
    """

    def __init__(
        self, content: str, version: FeedVersion = FeedVersion.RSS_2_0
    ):
        self.content = content

        # Check the version
        if (
            not isinstance(version, FeedVersion)
            or version not in FeedVersion.supported()
        ):
            raise FeedVersionError(
                version=version, supported=FeedVersion.supported()
            )
        self.version = version
        self.__etag: Optional[str] = None

    @property
    def etag(self) -> str:
        """Return a unique ETag for the feed content.

        Returns
        -------
        str
            Calculated etag.
        """
        if self.__etag is None:
            self.__etag = utils.etag(self.content)
        return self.__etag

    @property
    def content_type(self) -> str:
        """Return the content_type for the feed.

        Returns
        -------
        str
            Content type.
        """
        if self.version in (
            FeedVersion.RSS_0_91,
            FeedVersion.RSS_1_0,
            FeedVersion.RSS_2_0,
        ):
            return "application/rss+xml"
        elif self.version in (FeedVersion.ATOM_1_0,):
            return "application/atom+xml"
        else:
            return "application/xml"
