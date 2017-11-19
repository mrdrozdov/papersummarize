from datetime import datetime

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Float,
    Text,
    DateTime,
)
from sqlalchemy.orm import relationship
from sqlalchemy import event

from .meta import Base


class PaperRating(Base):
    """ The SQLAlchemy declarative model class for a PaperRating object. """
    __tablename__ = 'paper_ratings'
    id = Column(Integer, primary_key=True)
    paper_id = Column(ForeignKey('papers.id'), nullable=False)
    value = Column(Float, nullable=False, default=0.)
    count = Column(Integer, nullable=False, default=0)
    paper = relationship('Paper', backref='rating')
