from datetime import datetime

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Text,
    DateTime,
)
from sqlalchemy.orm import relationship
from sqlalchemy.orm import object_session

from .meta import Base


class Tag(Base):
    """ The SQLAlchemy declarative model class for a Tag object. """
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    paper_id = Column(ForeignKey('papers.id'), nullable=False)
    creator_id = Column(ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    unique_name = Column(Text, unique=True) # TODO: Must be a simpler way to enforce unique with multiple columns.
    name = Column(Text)
    creator = relationship('User', backref='created_tags')
    paper = relationship('Paper', backref='created_tags')

    def set_name(self, name):
        self.name = name
        unique_name = 'ARXIVID_{}_USERNAME_{}_TAGNAME_{}'.format(self.paper.arxiv_id, self.creator.name, name)

        if object_session(self).query(Tag).filter_by(unique_name=unique_name).first() is not None:
            raise ValueError("Tag with unique_name='{}' already exists.".format(unique_name))

        self.unique_name = unique_name

