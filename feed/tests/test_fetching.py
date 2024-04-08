from arxiv.taxonomy.definitions import CATEGORIES, ARCHIVES


from feed.errors import FeedIndexerError
from feed.fetch_data import validate_request,create_document
from feed.database import get_announce_papers

from unittest.mock import patch
import pytest
from datetime import  date

math=ARCHIVES["math"]
cs=ARCHIVES["cs"]
cs_cv=CATEGORIES["cs.CV"]

def test_no_request_cat():
    with pytest.raises(FeedIndexerError) as excinfo:
        validate_request("   ")
    assert "Invalid archive specification" in str(excinfo.value)
    with pytest.raises(FeedIndexerError) as excinfo:
        validate_request("cs.ai+")
    assert "Invalid archive specification" in str(excinfo.value)

def test_categories_not_case_sensitive():
    expected= ([],[CATEGORIES["cs.AI"]])
    assert validate_request("cs.ai") == expected
    assert validate_request("CS.ai") == expected
    assert validate_request("cs.AI") == expected
    assert validate_request("CS.AI") == expected

    expected= ([ARCHIVES["physics"]],[])
    assert validate_request("physics") == expected
    assert validate_request("PhYsiCs") == expected

def test_seperates_categories_and_archives():
    assert validate_request("cs.CV+math+hep-lat+cs.CG")==([math,ARCHIVES["hep-lat"]],[cs_cv,CATEGORIES["cs.CG"]])

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

def test_create_document(sample_arxiv_metadata, sample_doc,sample_author, sample_author2):
    #simple
    assert sample_doc==create_document(("new",sample_arxiv_metadata))
    #multiple authors
    sample_doc.authors=[sample_author,sample_author2]
    sample_arxiv_metadata.authors="Very Real Sr. (Cornell University), L Emeno"
    assert sample_doc==create_document(("new",sample_arxiv_metadata))

def test_basic_db_query(app):
    last_date=date(2023,10,26)
    first_date=date(2023,10,26)
    category=[cs_cv]
    with app.app_context():
        items=get_announce_papers(first_date, last_date, [],category)
    #any data is returned
    assert len(items) >0
    for item in items:
        action, meta= item
        #no absonly entries
        assert action != "absonly"
        #no updates with a version above 4
        assert action != "replace" or meta.version <5
        #correct category
        assert "cs.CV" in meta.abs_categories


def test_db_date_range(app):
    last_date=date(2023,10,27)
    first_date=date(2023,10,26)
    category=[cs_cv]
    with app.app_context():
        items=get_announce_papers(first_date, last_date, [],category)
    
    assert len(items) >=2 #two valid entries in database
    found_26=False
    found_27=False
    for item in items:
        
        action, meta= item
        if meta.document_id==12346:
            found_26=True
        if meta.document_id==12347:
            found_27=True
    assert found_26 
    assert found_27

def test_db_archive(app):
    last_date=date(2023,10,26)
    first_date=date(2023,10,26)
    archive=[cs]
    with app.app_context():
        items=get_announce_papers(first_date, last_date, archive,[])
    assert len(items) >0 
    for item in items:
        action, meta= item
        assert "cs." in meta.abs_categories

def test_db_multiple_archives(app):
    last_date=date(2023,10,26)
    first_date=date(2023,10,26)
    archives=[cs, math]
    with app.app_context():
        items=get_announce_papers(first_date, last_date, archives,[])
    assert len(items) >0 
    found_cs=False
    found_math=False
    for item in items:
        action, meta= item
        assert any(archive.id in meta.abs_categories for archive in archives)
        if "math." in meta.abs_categories:
            found_math=True
        if "cs.CV" in meta.abs_categories:
            found_cs=True
    assert found_cs and found_math

def test_db_multiple_categories(app):
    last_date=date(2023,10,26)
    first_date=date(2023,10,26)
    cats=[cs_cv, CATEGORIES["math.NT"]]
    with app.app_context():
        items=get_announce_papers(first_date, last_date, [],cats)
    assert len(items) >0 
    found_cs=False
    found_math=False
    for item in items:
        action, meta= item
        assert any(cat.id in meta.abs_categories for cat in cats)
        if "math.NT" in meta.abs_categories:
            found_math=True
        if "cs.CV" in meta.abs_categories:
            found_cs=True
    assert found_cs and found_math

def test_db_cat_and_archive(app):
    last_date=date(2023,10,26)
    first_date=date(2023,10,26)
    cat=[cs_cv]
    archive=[math]
    with app.app_context():
        items=get_announce_papers(first_date, last_date, archive,cat)
    assert len(items) >0 
    found_cs=False
    found_math=False
    for item in items:
        action, meta= item
        if "math." in meta.abs_categories:
            found_math=True
        if "cs.CV" in meta.abs_categories:
            found_cs=True
    assert found_cs and found_math

def test_db_find_alias(app):
    #finds a paper only labeled with cs.IT
    last_date=date(2023,10,26)
    first_date=date(2023,10,26)
    category=[CATEGORIES["math.IT"]]
    with app.app_context():
        items=get_announce_papers(first_date, last_date, [],category)
    alias_found=False
    for item in items:
        action, meta= item
        if meta.document_id==2366646:
            alias_found=True
            assert action=="new"
    assert alias_found

def test_db_alias_in_archive(app):
    #cs.IT is also math.IT and should show up in the math archive
    last_date=date(2023,10,26)
    first_date=date(2023,10,26)
    archive=[math]
    with app.app_context():
        items=get_announce_papers(first_date, last_date, archive,[])
    alias_found=False
    for item in items:
        action, meta= item
        if meta.document_id==2366646:
            alias_found=True
            assert action=="new"
    assert alias_found

def test_db_identify_cross(app):
    last_date=date(2023,10,26)
    first_date=date(2023,10,26)
    category=[cs_cv]
    with app.app_context():
        items=get_announce_papers(first_date, last_date, [],category)
    item_found=False
    for item in items:
        action, meta= item
        if meta.document_id==12346:
            item_found=True
            assert action=="cross"
    assert item_found

def test_db_identify_repcross(app):
    last_date=date(2023,10,26)
    first_date=date(2023,10,26)
    category=[cs_cv]
    with app.app_context():
        items=get_announce_papers(first_date, last_date, [],category)
    item_found=False
    for item in items:   
        action, meta= item
        if meta.document_id==12345:
            item_found=True
            assert action=="replace-cross"
    assert item_found

def test_db_identify_replace(app):
    last_date=date(2023,10,26)
    first_date=date(2023,10,26)
    archive=[ARCHIVES["astro-ph"]]
    with app.app_context():
        items=get_announce_papers(first_date, last_date, archive,[])
    item_found=False
    for item in items:   
        action, meta= item
        if meta.document_id==12345:
            item_found=True
            assert action=="replace"
    assert item_found

def test_db_identify_new(app):
    last_date=date(2023,10,25)
    first_date=date(2023,10,25)
    archive=[ARCHIVES["astro-ph"]]
    with app.app_context():
        items=get_announce_papers(first_date, last_date, archive,[])
    item_found=False
    for item in items:   
        action, meta= item
        if meta.document_id==12345:
            item_found=True
            assert action=="new"
    assert item_found

def test_db_announce_type_order(app):
    #the papers returning in backwards order means they will be printed in the correct order
    last_date=date(2023,10,27)
    first_date=date(2023,10,26)
    archive=[math,cs]
    with app.app_context():
        items=get_announce_papers(first_date, last_date, archive,[])

    order={"new":4, "cross":3, "replace":2, "replace-cross":1}
    current_min=1
    last_id="9999.99999"
    for item in items:   
        action, meta= item
        score=order[action]
        assert score >= current_min
        if score > current_min:
            current_min=score
            last_id=meta.paper_id
        else: #ordered by paper id within same type
            assert meta.paper_id < last_id
            last_id=meta.paper_id

