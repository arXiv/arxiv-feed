#!/bin/bash

## Variables
export PIPENV_VERBOSITY=-1

PROJECT=feed
if [ -z ${MIN_PYLINT_SCORE} ]; then
  MIN_PYLINT_SCORE="9";
fi

if [ -z ${REPORT_TO_TRAVIS} ]; then
  REPORT_TO_TRAVIS=0;
fi

if [ -z ${TRAVIS_PULL_REQUEST_SHA} ];  then
  SHA=${TRAVIS_COMMIT};
else
  SHA=${TRAVIS_PULL_REQUEST_SHA};
fi


## Functions

# Report execution to travis.
#
# Args:
#   context:     `flake8`, `pylint`, `mypy` or `pydocstyle`.
#   state:       `success` or `failure`.
#   description: Custom description.
report_to_travis () {
  if [ ${REPORT_TO_TRAVIS} = 1 ]; then
    local JSON=$(printf '{"context": "code-quality/%s", "state": "%s", "description": "%s", "target_url": "https://travis-ci.org/%s/builds/%s"}' ${1} ${2} ${3} ${TRAVIS_REPO_SLUG} ${TRAVIS_BUILD_ID});
  	curl -u ${USERNAME}:${GITHUB_TOKEN}                                           \
  	     -d \'${JSON}\'                                                           \
         -XPOST https://api.github.com/repos/${TRAVIS_REPO_SLUG}/statuses/${SHA}  \
         > /dev/null 2>&1;
  fi
}


# Run a simple status reported command.
#
# Args:
#   command: Command to run.
status_command () {
  pipenv run ${1} ${PROJECT}
  if [ $? = 0 ]; then
    local STATE="success" && echo "${1} passed";
  else
    local STATE="failure" && echo "${1} failed";
  fi

  report_to_travis ${1} ${STATE} ""
}


## flake8
status_command flake8


## pydocstyle
status_command pydocstyle


## mypy
status_command mypy


## pylint
PYLINT_SCORE=$(pipenv run pylint ${PROJECT} | tail -2 | grep -Eo '[0-9\.]+/10' | tail -1 | sed s/\\/10//)
PYLINT_PASS=$(echo $PYLINT_SCORE">="$MIN_PYLINT_SCORE | bc -l)
if [ ${PYLINT_PASS} = 1 ]; then
  PYLINT_STATE="success" && echo "pylint passed with score ${PYLINT_SCORE}/10";
else
  PYLINT_STATE="failure" && echo "pylint failed with score ${PYLINT_SCORE}/10";
fi

report_to_travis pylint ${PYLINT_STATE} "${PYLINT_SCORE}/10"
