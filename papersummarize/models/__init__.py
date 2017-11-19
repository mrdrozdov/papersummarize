from sqlalchemy import engine_from_config
from sqlalchemy import event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import configure_mappers
from sqlalchemy.orm.session import Session
import zope.sqlalchemy

# import or define all models here to ensure they are attached to the
# Base.metadata prior to any initialization routines
from .page import Page  # flake8: noqa
from .paper import Paper  # flake8: noqa
from .paper_rating import PaperRating  # flake8: noqa
from .user_paper_rating import UserPaperRating  # flake8: noqa
from .tag import Tag  # flake8: noqa
from .tip import Tip  # flake8: noqa
from .user import User  # flake8: noqa

# run configure_mappers after defining all of the models to ensure
# all relationships can be setup
configure_mappers()


def get_engine(settings, prefix='sqlalchemy.'):
    return engine_from_config(settings, prefix)


def get_session_factory(engine):
    factory = sessionmaker()
    factory.configure(bind=engine)
    return factory


def get_tm_session(session_factory, transaction_manager):
    """
    Get a ``sqlalchemy.orm.Session`` instance backed by a transaction.

    This function will hook the session to the transaction manager which
    will take care of committing any changes.

    - When using pyramid_tm it will automatically be committed or aborted
      depending on whether an exception is raised.

    - When using scripts you should wrap the session in a manager yourself.
      For example::

          import transaction

          engine = get_engine(settings)
          session_factory = get_session_factory(engine)
          with transaction.manager:
              dbsession = get_tm_session(session_factory, transaction.manager)

    """
    dbsession = session_factory()
    zope.sqlalchemy.register(
        dbsession, transaction_manager=transaction_manager)
    return dbsession


def includeme(config):
    """
    Initialize the model for a Pyramid app.

    Activate this setup using ``config.include('papersummarize.models')``.

    """
    settings = config.get_settings()
    settings['tm.manager_hook'] = 'pyramid_tm.explicit_manager'

    # use pyramid_tm to hook the transaction lifecycle to the request
    config.include('pyramid_tm')

    # use pyramid_retry to retry a request when transient exceptions occur
    config.include('pyramid_retry')

    session_factory = get_session_factory(get_engine(settings))
    config.registry['dbsession_factory'] = session_factory

    # make request.dbsession available for use in Pyramid
    config.add_request_method(
        # r.tm is the transaction manager used by pyramid_tm
        lambda r: get_tm_session(session_factory, r.tm),
        'dbsession',
        reify=True
    )


#####################
# PaperRating Hooks #
#####################


def score(total, count):
    """
    TODO: C, m should be dynamically updated to reflect
    the mean score across all papers (C) and the mean
    count (m) in the top N papers.
    """
    R = total
    v = count
    C = 7.0
    m = 100

    W = (R*v + C*m) / float(v+m)

    return W


# TODO: Very inefficient...
def increase_value(paper_rating, user_paper_ratings):
    total = sum(map(lambda x: x.rating, user_paper_ratings))
    paper_rating.count = len(user_paper_ratings)
    paper_rating.value = score(total, paper_rating.count)


# TODO: Very inefficient...
def decrease_value(paper_rating, user_paper_ratings, user_paper_rating_to_remove):
    paper_rating.count = len(user_paper_ratings) - 1
    if paper_rating.count > 0:
        total = sum(map(lambda x: x.rating, user_paper_ratings)) - user_paper_rating_to_remove.rating
        paper_rating.value = score(total, paper_rating.count)
    else:
        paper_rating.value = 0.


@event.listens_for(Paper, 'after_insert')
def receive_after_insert(mapper, connection, target):
    """ listen for the 'after_insert' event """
    @event.listens_for(Session, "before_commit", once=True)
    def receive_before_commit(session):
        paper_rating = PaperRating(paper_id=target.id)
        session.add(paper_rating)


@event.listens_for(UserPaperRating, 'after_insert')
def receive_after_insert(mapper, connection, target):
    """ listen for the 'after_insert' event """
    @event.listens_for(Session, "before_commit", once=True)
    def receive_before_commit(session):
        paper_rating = session.query(PaperRating).filter_by(paper_id=target.paper_id).first()
        user_paper_ratings = session.query(UserPaperRating).filter_by(paper_id=target.paper_id).all()
        increase_value(paper_rating, user_paper_ratings)


@event.listens_for(UserPaperRating, 'after_delete')
def receive_after_delete(mapper, connection, target):
    """ listen for the 'after_delete' event """
    @event.listens_for(Session, "before_commit", once=True)
    def receive_before_commit(session):
        paper_rating = session.query(PaperRating).filter_by(paper_id=target.paper_id).first()
        user_paper_ratings = session.query(UserPaperRating).filter_by(paper_id=target.paper_id).all()
        decrease_value(paper_rating, user_paper_ratings, target)
