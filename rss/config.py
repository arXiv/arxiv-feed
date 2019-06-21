"""Flask configuration."""

import os

VERSION = '0.2'

SECRET_KEY = os.environ.get('SECRET_KEY', 'asdf1234')
SERVER_NAME = os.environ.get('RSS_SERVER_NAME')

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', 'nope')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', 'nope')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

LOGFILE = os.environ.get('LOGFILE')
LOGLEVEL = os.environ.get('LOGLEVEL', 20)

SQLALCHEMY_DATABASE_URI = os.environ.get('RSS_SQLALCHEMY_DATABASE_URI',
                                         'sqlite:///rss.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

JWT_SECRET = os.environ.get('JWT_SECRET', 'foosecret')

BASE_SERVER = os.environ.get('BASE_SERVER', 'arxiv.org')

METADATA_ENDPOINT = os.environ.get('METADATA_ENDPOINT',
                                   'https://beta.arxiv.org/')

RSS_NUM_DAYS = os.environ.get('RSS_NUM_DAYS', '1')

URLS = [
    ("pdf", "/pdf/<arxiv:paper_id>v<string:version>", BASE_SERVER),
    ("abs", "/abs/<arxiv:paper_id>v<string:version>", BASE_SERVER),
    ("abs_by_id", "/abs/<arxiv:paper_id>", BASE_SERVER),
    ("pdf_by_id", "/pdf/<arxiv:paper_id>", BASE_SERVER),
    ("pdfonly", "/pdf/<arxiv:paper_id>v<string:version>", BASE_SERVER),
]
