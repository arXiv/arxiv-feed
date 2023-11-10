from typing import List
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_
from feed.tables import ArXivUpdate,db
from datetime import datetime

def get_announce_papers(first_day: datetime, last_day:datetime, archives: List[str], categories: List[str] ) -> List[ArXivUpdate]:
    version_threshold = 4
    result_limit=15
    
    query_result = ArXivUpdate.query.filter(
        or_(
            ArXivUpdate.category.in_(categories),
            ArXivUpdate.archive.in_(archives)
        ),
        ~and_(
            ArXivUpdate.action == "replace",
            ArXivUpdate.version > version_threshold
        ),
        ArXivUpdate.action != "abs_only",
    ArXivUpdate.date >= first_day,
    ArXivUpdate.date <= last_day  # Inclusive upper bound
    ).limit(result_limit).all()

    #TODO any error handling?
    return query_result
        
def db_testing():
    db=current_app.extensions['sqlalchemy'].db

    categories_to_filter = []  # Add your desired categories to this list
    archives_to_filter = ['hep-lat']  # Add your desired archives to this list
    start_date=datetime(2021, 1, 15)
    end_date=datetime(2023, 1, 31)
    
    query_result=get_announce_papers(start_date,end_date,archives_to_filter,categories_to_filter)

    print("done")
    for item in query_result:
        print(item)
 
    return
