from feed.consts import FeedVersion


class FeedError(Exception):
    """Base RSS service exception.

    Parameters
    ----------
    error : str
        The error message.
    """

    def __init__(self, error: str = ""):
        self.error = error

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.error})"

    __repr__ = __str__


class FeedVersionError(FeedError):
    """Invalid feed version."""

    def __init__(self, version: str):
        super().__init__(
            error=f"Unsupported RSS version '{version}' requested."
            f"Valid options are: {', '.join(FeedVersion)}."
        )


class FeedIndexerError(FeedError):
    """An exception for returning errors from the RSS feed's indexer."""

    pass
