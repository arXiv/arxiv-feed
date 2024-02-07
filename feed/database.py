from typing import List, Tuple, Optional
from datetime import date
import logging 

from sqlalchemy.orm import aliased
from sqlalchemy.orm.query import Query
from sqlalchemy import and_, or_, case, desc
from sqlalchemy.sql import func

from arxiv import taxonomy
from arxiv.taxonomy.definitions import CATEGORIES

from feed.tables import db, ArXivUpdate, ArXivMetadata, DocumentCategory
from feed.consts import UpdateActions

logger = logging.getLogger(__name__)

def get_announce_papers(first_day: date, last_day: date, archives: List[str], categories: List[str])->List[Tuple[UpdateActions, ArXivMetadata]]:
    result_limit = 2000
    version_threshold = 6

    category_list=_all_possible_categories(archives, categories)

    up=aliased(ArXivUpdate)
    case_order = case(
        [
            (up.action == 'new', 0),
            (up.action == 'cross', 1),
            (up.action == 'replace', 2),
        ],
        else_=3 
    ).label('case_order')
 
    doc_ids=(
        db.session.query(
            up.document_id,
            up.action
        )
        .filter(up.date.between(first_day, last_day))
        .filter(up.action!="absonly")
        .filter(or_(up.action != 'replace', up.version < version_threshold)) #replacements below a certain version
        .filter(up.category.in_(category_list))
        .group_by(up.document_id) #one listings per paper
        .order_by(case_order) #action kept chosen by priority if multiple
        .subquery() 
    )

    dc = aliased(DocumentCategory)
    #all listings for the specific category set
    all = (
        db.session.query(
            doc_ids.c.document_id, 
            doc_ids.c.action,  
            func.max(dc.is_primary).label('is_primary')
        )
        .join(dc, dc.document_id == doc_ids.c.document_id)
        .where(dc.category.in_(category_list))
        .group_by(dc.document_id) 
        .subquery() 
    )

    #sorting and counting by type of listing
    listing_type = case(
        [
            (and_(all.c.action == 'new', all.c.is_primary == 1), 'new'),
            (or_(all.c.action == 'new', all.c.action == 'cross'), 'cross'),
            (and_(all.c.action == 'replace', all.c.is_primary == 1), 'replace'),
            (all.c.action == 'replace', 'replace-cross')
        ],
        else_="no_match"
    ).label('listing_type')

    listing_order = case(
        [
            (listing_type == 'new', 4),
            (listing_type == 'cross', 3),
            (listing_type == 'replace', 2),
            (listing_type == 'replace-cross', 1),
        ],
        else_=0 
    ).label('case_order')

    #data for listings to be displayed
    meta = aliased(ArXivMetadata)
    result_query = (
        db.session.query(
            listing_type,
            meta
        )
        .join(meta, meta.document_id == all.c.document_id)
        .filter(meta.is_current ==1)
        .order_by(listing_order, meta.paper_id.desc())
        .limit(result_limit) 
    )

    results=result_query.all()
    
    if len(results) <1:
        str=f"No results for db query. first day: {first_day}, last day: {last_day}, archives: {archives}, categories: {categories}\n"
        _debug_no_response(str,result_query)
       

    return results # type: ignore

def _all_possible_categories(archives:List[str], categories:List[str]) -> List[str]:
    """returns a set of all categories in the lists of archvies and categories, 
    this includes alternate names of categories from aliases and subsumed archives
    """
    total_set=set()
    for archive in archives:
        total_set.update(get_categories_from_archive(archive))
    for category in categories:
        total_set.add(category)
        second_name=_check_alternate_name(category)
        if second_name:
            total_set.add(second_name)
    return list(total_set)
    
def get_categories_from_archive(archive:str) ->List[str]:
    """returns a list names of all categories under an archive
    includes older names that make no longer be active
    """
    list=[]
    for category in CATEGORIES.keys():
        if CATEGORIES[category]["in_archive"] == archive:
            list.append(category)
            second_name=_check_alternate_name(category)
            if second_name:
                list.append(second_name)

    return list

def _check_alternate_name(category:str) -> Optional[str]:
    # returns alternate name for aliases
    #returns previous name if archive was subsumed

    #check for aliases
    for key, value in taxonomy.CATEGORY_ALIASES.items():
        if category == key: #old alias name provided
            return value # type: ignore
        elif category == value: #new alias name provided
            return key # type: ignore
        
    #check for subsumed archives
    for key, value in taxonomy.ARCHIVES_SUBSUMED.items():
        if category == value: #has old archive name
            return key # type: ignore

    return None #no alternate names

def _debug_no_response(msg:str, query: Query)->None:
    
    actual_query=str(query.statement.compile(compile_kwargs={"literal_binds": True}))
    
    recent_entry = (
        db.session.query(ArXivUpdate)
        .order_by(desc(ArXivUpdate.date))
        .first()
    )
    log=msg+f"most recent entry: {recent_entry}"
    logger.warning(log)
    return

def check_service() -> str:
    query=db.session.query(ArXivUpdate).limit(1).all()
    if len(query)==1:
        return "GOOD"
    return "BAD"