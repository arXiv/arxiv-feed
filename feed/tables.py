from sqlalchemy import MetaData, Integer, Column, Date, Enum, String, text, Index, ForeignKey, DateTime, Text
from flask_sqlalchemy import SQLAlchemy

metadata = MetaData()
db= SQLAlchemy()

class ArXivUpdate(db.Model):
    __tablename__ = "arXiv_updates"
    __table_args__ = (db.PrimaryKeyConstraint('document_id', 'date', 'action', 'category'),)

    document_id = Column(
        ForeignKey("arXiv_documents.document_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
        server_default=text("'0'"),
    )
    version=Column(Integer, nullable=False, server_default=text("'1'"))
    date=Column( Date, index=True)
    action=Column( Enum('new', 'replace', 'absonly', 'cross', 'repcro'))
    archive=Column(String(20), index=True)
    category=Column( String(20), index=True)

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