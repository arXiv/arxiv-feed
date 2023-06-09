# arXiv Feed

This is a RSS and Atom feed service that reads from the arxiv-search
ElasticSearch and produces feeds.

## Development environment

### Running Elasticsearch + Kibana with Docker Compose

A ``docker-compose.yml`` file is included in the root of this repo that will
start ElasticsSarch and Kibana on your local machine. This is for local
development and testing purposes only. You'll need to install
[Docker Compose](https://docs.docker.com/compose/).

The first time you run ES + Kibana, you'll need to build the local ES image.

```bash
docker-compose build
```

You can start ES + Kibana like this:

```bash
docker-compose up -d
```

You should be able to access Kibana at http://127.0.0.1:5601, and Elasticsearch
at http://127.0.0.1:9200.

### Adding documents to the index

The [arxiv-search](https://cul-it.github.io/arxiv-search) project has provided
a Docker image called
[arxiv/search-index](https://hub.docker.com/r/arxiv/search-index) that can be
used to add documents to the search index.

**Note:** To do this, you will need to be connected to Cornell VPN.

With Elasticsearch running using the ``docker-compose`` method, above, you
should be able to add documents to the index using (note that you'll need to
update paths):

```bash
make index
```

This runs the `arxiv/search-index` image in a container on the network created
using ``docker-compose``, above. The image accepts a single argument, the path
(within the container) of the text file containing paper IDs. To get the file
inside the container we use the `example` folder which is mounted inside the
container as `/example`. To specify paper ids just populate the `paper_ids.txt`
inside the example folder.


You can verify that the papers were indexed by running:

```
make index-test
```

Note: You'll need [jq](https://stedolan.github.io/jq/) installed to run this
command.


### Running the development server


To run the development enter:

```
make run
```

This will start the flask development server on port 5000.


For other commands run:

```
make help
```


### Pre-commit hooks

To run pre commit hooks install the dev dependencies:

```bash
pipenv install --dev
```

After that you'll need to install the pre commit hooks:

```bash
pipenv run pre-commit install
```

Git will run all the pre-commit hooks on all changed files before you are
allowed to commit. You will be allowed to commit only if all checks pass.

You can also run the pre commit hooks manually with:

```bash
pipenv run pre-commit run
```

### CURL to ES
Here is an example of using CURL to test a query against ES:

    curl -X GET --header 'Content-Type: application/json' \
    "https://search-something.arxiv.org/arxiv0.0/_search" \
    -d '{"query": {"bool": {"must": [{"wildcard": {"primary_classification.category.id": "physics.*"}}], "filter": [{"range": {"submitted_date": {"gte": "2023-06-08", "lte": "2023-06-09", "format": "date"}}}]}}}'
