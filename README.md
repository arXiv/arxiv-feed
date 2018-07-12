# arXiv RSS Feeds

## Development environment

### Running Elasticsearch + Kibana with Docker Compose

A ``docker-compose.yml`` file is included in the root of this repo that will
start Elasticsearch and Kibana on your local machine. This is for local
development and testing purposes only. You'll need to install
[Docker Compose](https://docs.docker.com/compose/).

The first time you run ES + Kibana, you'll need to build the local ES image.

```bash
docker-compose build
```

You can start ES + Kibana like this:

```bash
docker-compose up
```

You should be able to access Kibana at http://127.0.0.1:5601, and Elasticsearch
at http://127.0.0.1:9200.

### Adding documents to the index

The [arxiv-search](https://cul-it.github.io/arxiv-search) project has provided
a Docker image called
[arxiv/search-index](https://hub.docker.com/r/arxiv/search-index) that can be
used to add documents to the search index.

**Note:** To do this, you will need to be connected to Cornell VPN.

First, put the arXiv paper ID's that you'd like to index into a text file, one
ID per line. An example is included at ``example/paper_ids.txt``.

With Elasticsearch running using the ``docker-compose`` method, above, you
should be able to add documents to the index using (note that you'll need to
update paths):

```bash
docker run -e ELASTICSEARCH_HOST=arxiv-rss-elasticsearch \
    --network=arxivrss_es_stack \
    -v /Full/Path/To/arxiv-rss/example:/to_index \
    arxiv/search-index /to_index/paper_ids.txt
```

This runs the arxiv/search-index image in a container on the network created
using ``docker-compose``, above. The `-v` parameter mounts the directory that
contains your file with paper IDs onto the container at ``/to_index``.
The image accepts a single argument, the path (within the container) of the
text file containing paper IDs. In this example case, it would be
``/to_index/paper_ids.txt``.

You should see something like this:

```bash
Indexing 3 papers...
Papers indexed
2018-07-12 01:03:36,626 - search.agent.consumer - DEBUG: 1601.00121: get metadata
2018-07-12 01:03:36,627 - search.agent.consumer - DEBUG: 1601.00121: could not retrieve from cache: No cached document
2018-07-12 01:03:36,628 - search.agent.consumer - DEBUG: 1601.00121: requesting metadata
2018-07-12 01:03:36,916 - search.agent.consumer - DEBUG: current version is 1
2018-07-12 01:03:36,916 - search.agent.consumer - DEBUG: 1601.00122: get metadata
2018-07-12 01:03:36,918 - search.agent.consumer - DEBUG: 1601.00122: could not retrieve from cache: No cached document
2018-07-12 01:03:36,919 - search.agent.consumer - DEBUG: 1601.00122: requesting metadata
2018-07-12 01:03:37,167 - search.agent.consumer - DEBUG: current version is 1
2018-07-12 01:03:37,168 - search.agent.consumer - DEBUG: 1601.00123: get metadata
2018-07-12 01:03:37,169 - search.agent.consumer - DEBUG: 1601.00123: could not retrieve from cache: No cached document
2018-07-12 01:03:37,169 - search.agent.consumer - DEBUG: 1601.00123: requesting metadata
2018-07-12 01:03:37,428 - search.agent.consumer - DEBUG: current version is 2
2018-07-12 01:03:37,428 - search.agent.consumer - DEBUG: 1601.00123v1: get metadata
2018-07-12 01:03:37,428 - search.agent.consumer - DEBUG: 1601.00123v1: could not retrieve from cache: No cached document
2018-07-12 01:03:37,428 - search.agent.consumer - DEBUG: 1601.00123v1: requesting metadata
2018-07-12 01:03:37,677 - search.services.index - DEBUG: init ES session for index "arxiv" at arxiv-rss-elasticsearch:9200

Done indexing 3 papers.
```
