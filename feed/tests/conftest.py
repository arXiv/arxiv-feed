import pytest

from feed.domain import Document, Author
from feed.factory import create_web_app
from feed.tables import ArXivMetadata, ArXivUpdate


@pytest.fixture
def app():
    return create_web_app()


#set of database data and matching documents
@pytest.fixture
def sample_arxiv_update():
    return ArXivUpdate(
    
    )

@pytest.fixture
def sample_author():
    return Author(
        full_name= "Very",
        last_name="Real",
        initials="Sr.",
        affiliations=["Cornell University"]
    )

@pytest.fixture
def sample_doc(sample_author):
    return Document(    
        arxiv_id="1234.5678",
        version=3,
        title="Mysteries of the Universe",
        abstract="This whole concept is abstract.",
        authors=[sample_author],
        categories=["astro-ph","math.NT"],
        license="http://creativecommons.org/licenses/by/4.0/",
        doi="10.0000/00-AAA0000",
        journal_ref="",
        update_type="new"
        )