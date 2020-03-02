"""Base class for RSS serializers."""

from abc import ABC, abstractmethod

from rss.domain import DocumentSet


class Serializer(ABC):  # pylint: disable=too-few-public-methods
    """Abstract base class for feed serializers."""

    def __init__(self: ABC):
        """Noop initialization."""
        pass

    @abstractmethod
    def get_feed(self: ABC, response: DocumentSet) -> str:
        """
        Serialize the provided search results.

        Parameters
        ----------
        response : DocumentSet
            The ElasticSearch search results to serialize.

        Returns
        -------
        data : Tuple[str, int]
            The serialized results of the search plus the operation's HTTP
            status code.

        """
        pass
