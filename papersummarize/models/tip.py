from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy.orm import relationship

from .meta import Base


class Tip(Base):
    """ The SQLAlchemy declarative model class for a Tip object. """
    __tablename__ = 'tips'
    id = Column(Integer, primary_key=True)
    paper_id = Column(ForeignKey('papers.id'), nullable=False)
    creator_id = Column(ForeignKey('users.id'), nullable=False)

    data = Column(Text, nullable=False)

    creator = relationship('User', backref='created_tips')
    paper = relationship('Paper', backref='created_tips')
