
from feed.errors import FeedIndexerError
from feed.fetch_data import validate_request,create_document

from unittest.mock import patch
import pytest

def test_no_request_cat():
    with pytest.raises(FeedIndexerError) as excinfo:
        validate_request("   ")
    assert "Invalid archive specification" in str(excinfo.value)
    with pytest.raises(FeedIndexerError) as excinfo:
        validate_request("cs.ai+")
    assert "Invalid archive specification" in str(excinfo.value)

def test_categories_not_case_sensitive():
    expected= ([],["cs.AI"])
    assert validate_request("cs.ai") == expected
    assert validate_request("CS.ai") == expected
    assert validate_request("cs.AI") == expected
    assert validate_request("CS.AI") == expected

    expected= (["physics"],[])
    assert validate_request("physics") == expected
    assert validate_request("PhYsiCs") == expected

def test_seperates_categories_and_archives():
    assert validate_request("cs.CV+math+hep-lat+cs.CG")==(["math","hep-lat"],["cs.CV","cs.CG"])

def test_bad_cat_requests():
    #bad category form
    with pytest.raises(FeedIndexerError) as excinfo:
        validate_request(".AI")
    assert "Bad archive ''." in str(excinfo.value)
    with pytest.raises(FeedIndexerError) as excinfo:
        validate_request("....AI")
    assert "Bad archive/subject class structure" in str(excinfo.value)
    with pytest.raises(FeedIndexerError) as excinfo:
        validate_request("cs.AI.revolutionary")
    assert "Bad archive/subject class structure" in str(excinfo.value)
    with pytest.raises(FeedIndexerError) as excinfo:
        validate_request("cs.AI.")
    assert "Bad archive/subject class structure" in str(excinfo.value)    

    #not an archive
    with pytest.raises(FeedIndexerError) as excinfo:
        validate_request("psuedo-science")
    assert "Bad archive 'psuedo-science'." in str(excinfo.value)
    with pytest.raises(FeedIndexerError) as excinfo:
        validate_request("psuedo-science.CS")
    assert "Bad archive 'psuedo-science'." in str(excinfo.value)
    with pytest.raises(FeedIndexerError) as excinfo:
        validate_request("cs.AI+psuedo-science")
    assert "Bad archive 'psuedo-science'." in str(excinfo.value) 

    #not a category
    with pytest.raises(FeedIndexerError) as excinfo:
        validate_request("physics.psuedo-science")
    assert "Bad subject class 'psuedo-science'." in str(excinfo.value)
    with pytest.raises(FeedIndexerError) as excinfo:
        validate_request("cs.AI+physics.psuedo-science")
    assert "Bad subject class 'psuedo-science'." in str(excinfo.value)

    #invalid combiantion   
    with pytest.raises(FeedIndexerError) as excinfo:
        validate_request("physics.AI")
    assert "Bad subject class 'AI'." in str(excinfo.value)

def test_create_document(sample_arxiv_metadata, sample_arxiv_update, sample_doc,sample_author, sample_author2):
    #simple
    assert sample_doc==create_document((sample_arxiv_update,sample_arxiv_metadata))
    #multiple authors
    sample_doc.authors=[sample_author,sample_author2]
    sample_arxiv_metadata.authors="Very Real Sr. (Cornell University), L Emeno"
    assert sample_doc==create_document((sample_arxiv_update,sample_arxiv_metadata))