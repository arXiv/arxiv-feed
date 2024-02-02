from typing import List, Tuple
import logging 
from sqlalchemy import and_, or_, case
from feed.tables import ArXivUpdate, ArXivMetadata
from datetime import date
from sqlalchemy.orm import aliased

logger = logging.getLogger(__name__)

def get_announce_papers(first_day: date, last_day: date, archives: List[str], categories: List[str])->List[Tuple[ArXivUpdate, ArXivMetadata]]:
    result_limit = 2000
    version_threshold = 4

    action_order = case(
    [
        (ArXivUpdate.action == "new", 5),
        (ArXivUpdate.action == "replace", 4),
        (ArXivUpdate.action == "repcross", 3),
        (ArXivUpdate.action == "cross", 2)
    ],
    else_=1  # Default order for other actions
)

    # Create an alias for ArXivMetadata table to distinguish between the two
    metadata_alias = aliased(ArXivMetadata)

    # Your modified query
    query_result = ArXivUpdate.query.join(metadata_alias, ArXivUpdate.document_id == metadata_alias.document_id).filter(
        or_(
            ArXivUpdate.category.in_(categories),
            ArXivUpdate.archive.in_(archives)
        ),
        and_(
            or_(
                ArXivUpdate.action != "replace",
                and_(
                    ArXivUpdate.action == "replace",
                    ArXivUpdate.version <= version_threshold
                )
            ),
            ArXivUpdate.action != "absonly",
            ArXivUpdate.date >= first_day,
            ArXivUpdate.date <= last_day,  # Inclusive upper bound
            metadata_alias.is_current == 1  # dont display multiple version in a day TODO v4 and v5 in same day once version is fixed
        )
    ).order_by(action_order).add_entity(metadata_alias).limit(result_limit).all()

    if len(query_result) <1:
        logger.warning(f"No results for db query. first day: {first_day}, last day: {last_day}, archives: {archives}, categories: {categories}")

    return query_result # type: ignore