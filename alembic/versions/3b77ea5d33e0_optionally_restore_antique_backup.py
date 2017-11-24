"""optionally restore antique backup

Revision ID: 3b77ea5d33e0
Revises: 624481091cfb
Create Date: 2017-11-23 22:13:29.751702

"""
from alembic import op
import sqlalchemy as sa

# custom
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import papersummarize.models as models


# revision identifiers, used by Alembic.
revision = '3b77ea5d33e0'
down_revision = '624481091cfb'
branch_labels = None
depends_on = None


def copy_table(session, model_cls):
    rows = session.query(model_cls).all()
    rows = list(map(lambda x: vars(x), rows))
    op.bulk_insert(model_cls.__table__, rows)


def upgrade():
    antique = os.environ.get('ALEMBIC_ANTIQUE_001', None)
    if antique is not None:
        url = 'sqlite:///' + antique
        print(url)
        engine = create_engine(url, echo=True)
        Session = sessionmaker(bind=engine)
        session = Session()

        class_names = ['Page', 'Paper', 'Tip', 'User', 'PaperRating', 'Tag', 'UserPaperRating',]

        for name in class_names:
            model_cls = eval('models.{}'.format(name))
            copy_table(session, model_cls)

        session.close()


def downgrade():
    import ipdb; ipdb.set_trace()
    pass
