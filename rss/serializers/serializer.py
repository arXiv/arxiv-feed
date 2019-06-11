"""Base class for RSS serializers."""

from abc import ABC, abstractmethod
from rss.domain import EPrintSet
from typing import Tuple


class Serializer(ABC):  # pylint: disable=too-few-public-methods
    """Abstract base class for RSS serializers that produce XML results."""

    def __init__(self: ABC):
        """Noop initialization."""
        pass

    @abstractmethod
    def get_xml(self: ABC, response: EPrintSet) -> Tuple[str, int]:
        """
        Serialize the provided search results.

        Parameters
        ----------
        response
            The Elasticsearch search results to serialize.

        Returns
        -------
        data : str
            The serialized results of the search.

        """
        pass
