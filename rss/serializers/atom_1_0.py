"""Serializer for Atom 1.0"""

from flask.json import jsonify
from typing import Tuple, Optional
from arxiv import status
from rss.serializers.serializer import Serializer
from elasticsearch_dsl.response import *


class Atom_1_0(Serializer):

    def get_xml(self, response: Response) -> Tuple[Optional[dict], int]:
        data = jsonify({'version': "atom 1.0"})
        status_code = status.HTTP_200_OK
        return data, status_code
