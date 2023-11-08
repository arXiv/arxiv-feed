import json
from typing import Optional

from feed import utils
from feed.consts import FeedVersion
from feed.errors import FeedVersionError


class Feed:
    """Representation of a feed.

    Parameters
    ----------
    content : bytes
        Feed xml content.
    version : FeedVersion
        Version of the feed specification.

    Raises
    ------
    FeedVersionError
        For invalid feed versions.
    """

    def __init__(
        self,
        content: bytes,
        status_code: int = 200,
        version: FeedVersion = FeedVersion.RSS_2_0,
    ):
        self.content = content
        self.status_code = status_code

        # Check the version
        if not isinstance(version, FeedVersion):
            raise FeedVersionError(version=version, supported=FeedVersion.supported())
        elif version not in FeedVersion.supported():
            raise FeedVersionError(version=version.value, supported=FeedVersion.supported())
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
        if self.version.is_rss:
            return "application/rss+xml"
        elif self.version.is_atom:
            return "application/atom+xml"
        else:
            return "application/xml"

    def to_string(self) -> str:
        """Serialize feed to string.

        This method is used for saving Feed objects in the Redis cache.
        """
        return json.dumps(
            {
                "content": self.content.decode("utf-8"),
                "status_code": self.status_code,
                "version": self.version.value,
            },
            indent=0,
        )

    @classmethod
    def from_string(cls, s: str) -> "Feed":
        """De-serialize feed object from string.

        This method is used for getting Feed objects out of Redis cache.
        """
        data = json.loads(s)
        return cls(
            content=data["content"].encode("utf-8"),
            status_code=data["status_code"],
            version=FeedVersion(data["version"]),
        )
