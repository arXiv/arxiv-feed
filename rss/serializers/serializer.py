"""Base class for RSS serializers"""

from abc import ABC, abstractmethod
from elasticsearch_dsl.response import Response


class Serializer(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def get_xml(self, response: Response):
        """
        Serializes the provided search results.

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

