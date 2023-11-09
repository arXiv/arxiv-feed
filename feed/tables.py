from sqlalchemy import MetaData, Integer, Column, Date, Enum, String, text, Index, Table
from flask_sqlalchemy import SQLAlchemy

metadata = MetaData()
db= SQLAlchemy()

arXiv_updates = Table(
    'arXiv_updates', metadata,
    Column('document_id', Integer(), index=True),
    Column('version', Integer(), nullable=False, server_default=text("'1'")),
    Column('date', Date, index=True),
    Column('action', Enum('new', 'replace', 'absonly', 'cross', 'repcro')),
    Column('archive', String(20), index=True),
    Column('category', String(20), index=True),
    Index('document_id', 'document_id', 'date', 'action', 'category', unique=True)
)

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