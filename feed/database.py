from typing import List, Tuple
from datetime import date
import logging 

from sqlalchemy.orm import aliased
from sqlalchemy.orm.query import Query
from sqlalchemy import and_, or_, case, desc
from sqlalchemy.sql import func

from arxiv.taxonomy.definitions import ARCHIVES_SUBSUMED
from arxiv.taxonomy.category import Archive, Category
from arxiv.db import session
from arxiv.db.models import Metadata, Updates, DocumentCategory

from feed.consts import UpdateActions

logger = logging.getLogger(__name__)

def get_announce_papers(first_day: date, last_day: date, archives: List[Archive], categories: List[Category])->List[Tuple[UpdateActions, Metadata]]:
    result_limit = 2000
    version_threshold = 6

    category_list=_all_possible_categories(archives, categories)

    up=aliased(Updates)
    case_order = case(
            (up.action == 'new', 0),
            (up.action == 'cross', 1),
            (up.action == 'replace', 2),
        else_=3 
    ).label('case_order')
 
    doc_ids=(
        session.query(
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
        session.query(
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
            (and_(all.c.action == 'new', all.c.is_primary == 1), 'new'),
            (or_(all.c.action == 'new', all.c.action == 'cross'), 'cross'),
            (and_(all.c.action == 'replace', all.c.is_primary == 1), 'replace'),
            (all.c.action == 'replace', 'replace-cross'),
        else_="no_match"
    ).label('listing_type')

    listing_order = case(
            (listing_type == 'new', 4),
            (listing_type == 'cross', 3),
            (listing_type == 'replace', 2),
            (listing_type == 'replace-cross', 1),
        else_=0 
    ).label('case_order')

    #data for listings to be displayed
    meta = aliased(Metadata)
    result_query = (
        session.query(
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
        archive_ids = ', '.join(archive.id for archive in archives)
        category_ids = ', '.join(category.id for category in categories)
        str=f"No results for db query. first day: {first_day}, last day: {last_day}, archives: [{archive_ids}], categories: [{category_ids}]\n"
        _debug_no_response(str,result_query)
       

    return results # type: ignore

def _all_possible_categories(archives:List[Archive], categories:List[Category]) -> List[str]:
    """returns a list of all category ids that may be relevant for list of archives and categories, 
    including aliases and previously subsumed archives
    """
    all=set()
    for archive in archives:
        for category in archive.get_categories(True):
            all.add(category.id)
            if category.alt_name and category.id not in ARCHIVES_SUBSUMED.keys():
                all.add(category.alt_name)
    for category in categories:
        all.add(category.id)
        if category.alt_name and category.id not in ARCHIVES_SUBSUMED.keys():
            all.add(category.alt_name)

    return list(all)


def _debug_no_response(msg:str, query: Query)->None:
    
    actual_query=str(query.statement.compile(compile_kwargs={"literal_binds": True}))
    
    recent_entry = (
        session.query(Updates)
        .order_by(desc(Updates.date))
        .first()
    )
    log=msg+f"most recent entry: {recent_entry}"
    logger.warning(log)
    return

def check_service() -> str:
    query=session.query(Updates).limit(1).all()
    if len(query)==1:
        return "GOOD"
    return "BAD"