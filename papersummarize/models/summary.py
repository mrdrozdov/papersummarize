from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy.orm import relationship

from .meta import Base
from ..shared.enums import ENUM_Summary_visibility, ENUM_Summary_review_status


class Summary(Base):
    """ The SQLAlchemy declarative model class for a Summary object. """
    __tablename__ = 'summaries'
    id = Column(Integer, primary_key=True)
    paper_id = Column(ForeignKey('papers.id'), nullable=False)
    creator_id = Column(ForeignKey('users.id'), nullable=False)
    visibility = Column(Text, nullable=False, default=ENUM_Summary_visibility['members'])
    review_status = Column(Text, nullable=False, default=ENUM_Summary_review_status['under_review'])

    data = Column(Text, nullable=False)

    creator = relationship('User', backref='created_summaries')
    paper = relationship('Paper', backref='created_summaries')
