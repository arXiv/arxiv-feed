from sqlalchemy import MetaData, Integer, Column, Date, Enum, String, text, Index, Table, ForeignKey, DateTime, Text
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

metadata = MetaData()
db= SQLAlchemy()


###models for the arxiv_updates table
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
        return f"ArXivUpdate(document_id={self.document_id}, version={self.version}, action={self.action}, date={self.date}, category={self.category}, archive={self.archive})"
    
### models for the arXiv_metadata table
class ArXivMetadata(db.Model):
    """Model for arXiv document metadata."""

    __tablename__ = "arXiv_metadata"
    __table_args__ = (Index("pidv", "paper_id", "version", unique=True),)

    metadata_id = Column(Integer, primary_key=True)
    document_id = Column(
        ForeignKey(
            "arXiv_documents.document_id", ondelete="CASCADE", onupdate="CASCADE"
        ),
        nullable=False,
        index=True,
        server_default=text("'0'"),
    )
    paper_id = Column(String(64), nullable=False)
    created = Column(DateTime)
    updated = Column(DateTime)
    submitter_id = Column(ForeignKey("tapir_users.user_id"), index=True)
    submitter_name = Column(String(64), nullable=False)
    submitter_email = Column(String(64), nullable=False)
    source_size = Column(Integer)
    source_format = Column(String(12))
    source_flags = Column(String(12))
    title = Column(Text)
    authors = Column(Text)
    abs_categories = Column(String(255))
    comments = Column(Text)
    proxy = Column(String(255))
    report_num = Column(Text)
    msc_class = Column(String(255))
    acm_class = Column(String(255))
    journal_ref = Column(Text)
    doi = Column(String(255))
    abstract = Column(Text)
    license = Column(ForeignKey("arXiv_licenses.name"), index=True)
    version = Column(Integer, nullable=False, server_default=text("'1'"))
    modtime = Column(Integer)
    is_current = Column(Integer, server_default=text("'1'"))
    is_withdrawn = Column(Integer, nullable=False, server_default=text("'0'"))

    #document = relationship("Document")
    #arXiv_license = relationship("License")
    #submitter = relationship("User")