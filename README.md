# arXiv Feed

This is a RSS and Atom feed service that reads from the production database and produces feeds.

## Development environment

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
### testing
testing can be run with pytest if dev packages are installed

```bash
pytest
```

### deploying
creating pull requests to the devlop branch should trigger builds and cloud run instances
arxiv-feed in development and arxiv-feed-beta in production

pushes to master branch should trigger build and deploy in arxiv-feed in production and devlopment NOT YET IMPLEMENTED

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