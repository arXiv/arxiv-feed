# arXiv Feed

This is a RSS and Atom feed service that reads from the production database and produces feeds.

## to install
poetry install

## to run
export CLASSIC_DB_URI='sqlite:///feed/tests/data/test_data.db'
python main.py

note that without a database connection running feed locally isn't very interesting, the most recent local data is 2023-20-27 in the math category

## to run connected to GCP databases
export SQLALCHEMY_DATABASE_URI to the main gcp database URI

## to test
export CLASSIC_DB_URI='sqlite:///feed/tests/data/test_data.db'

pytest

### deploying
a PR to develop should run tests and build and deploy arxiv-feed in GCP development

merging/pushing to develop should trigger a build in production GCP to arxiv-feed-beta

pushes to master branch should trigger build and deploy in arxiv-feed in production
