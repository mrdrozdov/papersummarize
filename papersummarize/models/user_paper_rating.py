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


class UserPaperRating(Base):
    """ The SQLAlchemy declarative model class for a UserPaperRating object. """
    __tablename__ = 'user_paper_ratings'
    id = Column(Integer, primary_key=True)
    paper_id = Column(ForeignKey('papers.id'), nullable=False)
    creator_id = Column(ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    rating = Column(Integer)

    unique_name = Column(Text, unique=True)
    creator = relationship('User', backref='created_user_paper_ratings')
    paper = relationship('Paper', backref='created_user_paper_ratings')

    def __init__(self, *args, **kwargs):
        super(UserPaperRating, self).__init__(*args, **kwargs)
        self.unique_name = 'ARXIVID_{}_USERNAME_{}'.format(self.paper.arxiv_id, self.creator.name)

    def set_rating(self, rating):
        rating = int(rating)
        assert rating >= 1 and rating <= 10
        self.rating = rating
