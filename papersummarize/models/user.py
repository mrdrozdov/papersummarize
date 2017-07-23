import bcrypt
from sqlalchemy import (
    Column,
    Integer,
    Text,
)

from .meta import Base
from ..shared.enums import ENUM_User_standing, ENUM_User_is_leader


class User(Base):
    """ The SQLAlchemy declarative model class for a User object. """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False, unique=True)
    role = Column(Text, nullable=False)
    is_leader = Column(Integer, nullable=False, default=ENUM_User_is_leader['False']) # TODO: Use a boolean type.
    standing = Column(Integer, nullable=False, default=ENUM_User_standing['neutral_standing'])

    password_hash = Column(Text)

    def set_password(self, pw):
        pwhash = bcrypt.hashpw(pw.encode('utf8'), bcrypt.gensalt())
        self.password_hash = pwhash.decode('utf8')

    def check_password(self, pw):
        if self.password_hash is not None:
            expected_hash = self.password_hash.encode('utf8')
            return bcrypt.checkpw(pw.encode('utf8'), expected_hash)
        return False
