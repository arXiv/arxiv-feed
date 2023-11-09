from sqlalchemy import MetaData, Integer, Column, Date, Enum, String, text, Index, Table

metadata = MetaData()

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
