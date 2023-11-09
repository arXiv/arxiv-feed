from flask import current_app
from flask_sqlalchemy import SQLAlchemy

#from arxiv_db.models.associative_tables import t_arXiv_updates
from feed.tables import arXiv_updates
from datetime import datetime

db= SQLAlchemy()


class ArXivUpdate(db.Model):
    __table__ = arXiv_updates
    # Define the composite primary key
    __table_args__ = (
        db.PrimaryKeyConstraint('document_id', 'date', 'action', 'category'),
    )
    # Explicitly specify primary key columns
    __mapper_args__ = {
        'primary_key': [arXiv_updates.c.document_id, arXiv_updates.c.date, arXiv_updates.c.action, arXiv_updates.c.category]
    }
    # You can define indexes and additional attributes here
    def __repr__(self):
        return f"ArXivUpdate(document_id={self.document_id}, date={self.date}, ...)"

        
def db_testing():
    db=current_app.extensions['sqlalchemy'].db
    #db.create_all()

    #create_updates()
 
    print(ArXivUpdate.query.limit(2).all())
 
    return

def create_updates():
    new_update1 = ArXivUpdate(
        document_id=12345,
        version=2,
        date=datetime.strptime('2023-10-25', '%Y-%m-%d'),
        action='new',
        archive='arXiv',
        category='cs.CV'  # Replace with the appropriate category
    )
    
    new_update2 = ArXivUpdate(
        document_id=12346,
        version=2,
        date=datetime.strptime('2023-10-26', '%Y-%m-%d'),
        action='new',
        archive='arXiv',
        category='cs.CV'  # Replace with the appropriate category
    )

    new_update3 = ArXivUpdate(
        document_id=12347,
        version=2,
        date=datetime.strptime('2023-10-27', '%Y-%m-%d'),
        action='new',
        archive='arXiv',
        category='cs.CV'  # Replace with the appropriate category
    )

    db.session.add(new_update1)
    db.session.add(new_update2)
    db.session.add(new_update3)
    db.session.commit()
    return