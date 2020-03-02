from rss.consts import FeedVersion


class FeedError(Exception):
    """Base RSS service exception.

    Parameters
    ----------
    message : str
        The error message.
    """

    def __init__(self, message=""):
        self.message = message

    def __str__(self):
        return f"{self.__class__.__name__}(message={self.message})"

    __repr__ = __str__


class FeedVersionError(FeedError):
    """Invalid feed version."""

    def __init__(self, version: str):
        super().__init__(
            message=f"Unsupported RSS version '{version}' requested."
            f"Valid options are: {', '.join(FeedVersion)}."
        )


class FeedIndexerError(FeedError):
    """An exception for returning errors from the RSS feed's indexer."""

    pass
