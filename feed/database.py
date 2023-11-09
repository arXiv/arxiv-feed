from flask import current_app
from flask_sqlalchemy import SQLAlchemy
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
        return f"ArXivUpdate(document_id={self.document_id}, version={self.version}, action={self.action}, date={self.date}, category={self.category})"

        
def db_testing():
    db=current_app.extensions['sqlalchemy'].db
 
    print(ArXivUpdate.query.limit(2).all())
 
    return
