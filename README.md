# arXiv RSS Feeds

## Development environment

### Running Elasticsearch + Kibana with Docker Com,pose

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

You should be able to
