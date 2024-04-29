# arXiv Feed

This is a RSS and Atom feed service that reads from the production database and produces feeds.

## to install
```
pip install poetry
poetry install
```
## to run locally
```
export CLASSIC_DB_URI='sqlite:///feed/tests/data/test_data.db'
python main.py
```
note that without a database connection running feed locally isn't very interesting, the most recent local data is 2023-20-27 in the math category

## to run connected to GCP databases
export CLASSIC_DB_URI to the main gcp database URI

## to test
```
export CLASSIC_DB_URI='sqlite:///feed/tests/data/test_data.db'
pytest
```

### deploying
a PR to develop should run tests and build and deploy arxiv-feed in GCP development

merging/pushing to develop should trigger a build in production GCP to arxiv-feed-beta

pushes to master branch should trigger build and deploy in arxiv-feed in production


### running in docker

build image with this command:

`docker build -t feed .`

## to run
Create a docker.env file with any enviroment variables you want to set. Here is an example one for running of the local database:

```
DEBUG=True
TESTING=True
FEED_NUM_DAYS=300
CLASSIC_DB_URI=sqlite:///feed/tests/data/test_data.db 
```
this can be run with
`docker run --env-file docker.env -p 8080:8080 feed`
