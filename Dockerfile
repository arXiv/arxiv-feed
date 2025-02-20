# arxiv/feed
#
# Defines the runtime for the arXiv feed service, which provides RSS and ATOM
# article feeds

FROM python:3.11 as base

ENV LC_ALL=en_US.utf8 \
    LANG=en_US.utf8

FROM base as python-deps

# Install python dependencies in /.venv
RUN python -m venv "/.venv"
ENV PATH="/.venv/bin:$PATH"

RUN pip install "poetry==1.3.2"
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

RUN pip install "gunicorn==20.1.0"

FROM base as runtime

# Copy virtual env from python-deps stage
WORKDIR /opt/arxiv
COPY --from=python-deps /.venv /.venv
ENV PATH="/.venv/bin:$PATH"

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    APP_HOME=/opt/arxiv


# add python application and configuration
ADD feed ./feed
RUN echo $git_commit > ./git-commit.txt

EXPOSE 8080

RUN useradd e-prints
USER e-prints

CMD exec gunicorn --bind :8080 --workers 1 --threads 8 --timeout 0 \
    "feed.factory:create_web_app()"
