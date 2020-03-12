.PHONY: help default deploy run test flake8 pydocstyle pydocstyle-travis pylint pylint-travis check check-travis format
.DEFAULT_GOAL := help
SHELL := /bin/bash
PROJECT := feed

.EXPORT_ALL_VARIABLES:
PIPENV_VERBOSITY = -1
ARXIV_FEED_CONFIGURATION = development


help:                   ## Show help.
	@grep -E '^[a-zA-Z2_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


# Index

index:                  ## Create and populate elasticsearch index.
	@docker run                                                          \
           --name=arxiv-search-index                                    \
    	   --network=arxiv_feed_network                                 \
    	   --volume `pwd`/example:/example                              \
    	   --env METADATA_ENDPOINT="$(METADATA_ENDPOINT)"               \
    	   --env ELASTICSEARCH_SERVICE_HOST=arxiv-feed-elasticsearch    \
    	   arxiv/search-index:0.6 /example/paper_ids.txt                \
    	   && echo "Indexing successful." || echo "Indexing failed."
	@docker rm --force arxiv-search-index


index-test:           ## Test if the index is created.
	@curl http://127.0.0.1:9200/arxiv/_search 2> /dev/null | jq '.hits.hits[]._source | {id: .id, title: .title, arxiv: .primary_classification.category.id}'

# Services

run:                    ## Run feed server in development mode.
	@FLASK_APP=app.py pipenv run flask run


# Utilities

test:                   ## Run tests and coverage checks.
	@pipenv run py.test -v --cov "$(PROJECT)" "$(PROJECT)"


check:                  ## Run code checks.
	bash lintstats.sh


format:                 ## Format the code.
	@pipenv run black --safe --target-version=py37 --line-length=79 "$(PROJECT)"
