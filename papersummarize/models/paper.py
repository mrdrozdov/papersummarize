from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Text,
    DateTime,
)
from sqlalchemy.orm import relationship

from .meta import Base


class Paper(Base):
    """ The SQLAlchemy declarative model class for a Paper object. """
    __tablename__ = 'papers'
    id = Column(Integer, primary_key=True)

    _rawid = Column(Text, nullable=False)
    _version = Column(Text, nullable=False)
    arxiv_id = Column(Text, nullable=False, unique=True)
    arxiv_comment = Column(Text)
    arxiv_primary_category = Column(Text)
    author = Column(Text, nullable=False)
    author_detail = Column(Text, nullable=False)
    authors = Column(Text)
    link = Column(Text, nullable=False)
    links = Column(Text)
    published = Column(DateTime, nullable=False)
    abstract = Column(Text) # summary
    tags = Column(Text)
    title = Column(Text, nullable=False)
    updated = Column(DateTime, nullable=False)
