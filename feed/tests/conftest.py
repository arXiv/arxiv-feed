import pytest
from datetime import datetime

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
        document_id=111111111111,
        version=3,
        date=datetime(2020, 1, 1, 0, 0, 0),
        action="new",
        archive="math",
        category="math.NT"
    )

@pytest.fixture
def sample_arxiv_metadata():
    return ArXivMetadata(
            metadata_id = 222222,
            document_id = 111111111111,
            paper_id = "1234.5678",
            created = datetime(2019, 10, 10, 0, 0, 0),
            updated = datetime(2019, 11, 11, 0, 0, 0),
            submitter_id = 111111,
            submitter_name = "Fake Person",
            submitter_email = "jake@fake.com",
            source_size = 300,
            source_format = "html",
            source_flags = "",
            title = "Mysteries of the Universe",
            authors = "Very Real Sr. (Cornell University)",
            abs_categories = "astro-ph math.NT",
            comments = "Very insightful",
            proxy = "",
            report_num = "",
            msc_class = "A",
            acm_class = "",
            journal_ref = "",
            doi = "10.0000/00-AAA0000",
            abstract = "This whole concept is abstract.",
            license = "http://creativecommons.org/licenses/by/4.0/",
            version = 3,
            modtime = 7,
            is_current = 1,
            is_withdrawn =0
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