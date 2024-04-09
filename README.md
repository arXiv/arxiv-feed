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





### below is things left over from the original build of feed - unsure of current use/ functionality, but keeping in case they are useful

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
