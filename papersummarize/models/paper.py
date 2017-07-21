from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy.orm import relationship

from .meta import Base


class Paper(Base):
    """ The SQLAlchemy declarative model class for a Paper object. """
    __tablename__ = 'papers'
    id = Column(Integer, primary_key=True)
    arxiv_id = Column(Text, nullable=False, unique=True)
