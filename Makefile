.PHONY: help default deploy run test flake8 pydocstyle pydocstyle-travis pylint pylint-travis check check-travis format
.DEFAULT_GOAL := help
SHELL := /bin/bash
PROJECT := feed

.EXPORT_ALL_VARIABLES:
PIPENV_VERBOSITY = -1
ARXIV_FEED_CONFIGURATION = development
METADATA_ENDPOINT = https://beta.arxiv.org


help:                   ## Show help.
	@grep -E '^[a-zA-Z2_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


# Services

run:                    ## Run feed server in development mode.
	@FLASK_APP=app.py pipenv run flask run


# Utilities

test:                   ## Run tests and coverage checks.
	@ARXIV_FEED_CONFIGURATION=testing pipenv run py.test -v --cov "$(PROJECT)" "$(PROJECT)"


check:                  ## Run code checks.
	bash lintstats.sh


format:                 ## Format the code.
	@pipenv run black --safe --target-version=py37 --line-length=79 "$(PROJECT)"

docker: 
	docker build -f Dockerfile -t arxiv-feed-app . 