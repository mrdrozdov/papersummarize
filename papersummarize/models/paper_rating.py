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
from ..shared.enums import ENUM_Summary_visibility, ENUM_Summary_review_status


class PaperRating(Base):
    """ The SQLAlchemy declarative model class for a PaperRating object. """
    __tablename__ = 'paper_ratings'
    id = Column(Integer, primary_key=True)
    paper_id = Column(ForeignKey('papers.id'), nullable=False)
    creator_id = Column(ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    rating = Column(Integer)

    unique_name = Column(Text, unique=True)
    creator = relationship('User', backref='created_paper_ratings')
    paper = relationship('Paper', backref='created_paper_ratings')

    def set_rating(self, rating):
        rating = int(rating)
        assert rating >= 1 and rating <= 10
        self.rating = rating

        # TODO: Is there a better place to put this?
        self.unique_name = 'ARXIVID_{}_USERNAME_{}'.format(self.paper.arxiv_id, self.creator.name)
