from datetime import datetime

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Text,
    DateTime,
)
from sqlalchemy.orm import relationship

from .meta import Base


class Tip(Base):
    """ The SQLAlchemy declarative model class for a Tip object. """
    __tablename__ = 'tips'
    id = Column(Integer, primary_key=True)
    paper_id = Column(ForeignKey('papers.id'), nullable=False)
    creator_id = Column(ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    data = Column(Text, nullable=False)

    creator = relationship('User', backref='created_tips')
    paper = relationship('Paper', backref='created_tips')
