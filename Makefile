.PHONY: help default deploy run test flake8 pydocstyle pydocstyle-travis pylint pylint-travis check check-travis format
.DEFAULT_GOAL := help
SHELL := /bin/bash
PROJECT := feed

.EXPORT_ALL_VARIABLES:
PIPENV_VERBOSITY = -1


# Arguments context,state,description
define report_to_travis
	curl -u $USERNAME:$GITHUB_TOKEN                                                                                                                                            \
    	 -d '{"context": "code-quality/$(1)", "state": "$(2)", "description": "$(3)", "target_url": "https://travis-ci.org/'$TRAVIS_REPO_SLUG'/builds/'$TRAVIS_BUILD_ID'"}'    \
         -XPOST https://api.github.com/repos/$TRAVIS_REPO_SLUG/statuses/$SHA                                                                                                   \
    	 > /dev/null 2>&1
endef


help:                              ## Show help.
	@grep -E '^[a-zA-Z2_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


# Services

run:                               ## Run feed server in development mode.
	@FLASK_APP=app.py pipenv run flask run


# Utilities

test:                              ## Run tests and coverage checks.
	@pipenv run py.test -v --cov "$(PROJECT)" "$(PROJECT)"


flake8:                            ## Run flake8 code check.
	@pipenv run flake8 "$(PROJECT)"


pydocstyle:                        ## Run pydocstyle check.
	@pipenv run pydocstyle "$(PROJECT)"


pydocstyle-travis:
	@pipenv run pydocstyle "$(PROJECT)"        && \
		$(call report_to_travis,pydocstyle,succeess,"")   || \
		$(call report_to_travis,pydocstyle,failure,"")


pylint:                            ## Run pylint code check.
	@pipenv run pylint "$(PROJECT)"


pylint-travis:
	$(eval PYLINT_SCORE := $(shell pipenv run pylint "$(PROJECT)" | tail -2 | grep -Eo '[0-9\.]+/10' | tail -1 | sed s/\\/10//))
	$(eval PYLINT_PASS := $(shell echo "$(PYLINT_SCORE) >= $$MIN_PYLINT_SCORE" | bc -l))
	@if [ $(PYLINT_PASS) == 0 ]; then                                   \
	     $(call report_to_travis,pylint,failure,"$(PYLINT_SCORE)/10");  \
	 else                                                               \
	     $(call report_to_travis,pylint,success,"$(PYLINT_SCORE)/10");  \
	fi


check: flake8 pydocstyle pylint    ## Run all code checks.


check-travis: flake8 pydocstyle-travis pylint-travis


format:                  ## Format the code.
	@pipenv run black --safe --target-version=py37 --line-length=79 "$(PROJECT)"
