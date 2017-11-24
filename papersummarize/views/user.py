from pyramid.compat import escape
import re
from docutils.core import publish_parts

from pyramid.httpexceptions import HTTPFound, HTTPNotFound

from pyramid.view import view_config

from .helpers.paper import paper_cell
from ..models import Tag, Tip, Paper, UserPaperRating
from ..shared import paper_utils
from ..shared.url_parsing import parse_arxiv_url

def most_recent(cls, session, user, page, limit):
    return session.query(cls)\
            .filter_by(creator=user)\
            .order_by(cls.created_at.desc())\
            .limit(limit)\
            .offset(page*limit)\
            .all()

@view_config(route_name='view_user', renderer='../templates/user_profile.jinja2')
def view_user(request):
    user = request.context.user
    return dict(user=user)

@view_config(route_name='view_user_activity', renderer='../templates/user_activity.jinja2')
def view_user_activity(request):
    # TODO: This filtering behavior is very weird...

    user = request.context.user
    limit = min(int(request.params.get('limit', 30)), 100)
    page = int(request.params.get('page', 0))

    tips = most_recent(Tip, request.dbsession, user, page, limit)
    tags = most_recent(Tag, request.dbsession, user, page, limit)
    user_paper_ratings = most_recent(UserPaperRating, request.dbsession, user, page, limit)
    activities = tips + tags + user_paper_ratings
    activities = reversed(sorted(activities, key=lambda x: x.created_at))

    def create_item_from_activity(a):
        item = dict()
        item['created_at'] = a.created_at
        item['paper'] = a.paper
        item['object'] = a

        if isinstance(a, Tip):
            item['type'] = 'tip'
        elif isinstance(a, Tag):
            item['type'] = 'tag'
        elif isinstance(a, UserPaperRating):
            item['type'] = 'user_paper_rating'
        else:
            item['type'] = 'unknown'

        return item

    activities = map(create_item_from_activity, activities)

    query_dict = dict(
        page_prev=max(page-1, 0),
        limit_prev=limit,
        page_next=page+1,
        limit_next=limit,
        )

    return dict(user=user, activities=activities, query=query_dict)

@view_config(route_name='view_user_taglist', renderer='../templates/user_taglist.jinja2')
def view_user_taglist(request):
    user = request.context.user
    limit = min(int(request.params.get('limit', 30)), 100)
    page = int(request.params.get('page', 0))

    tag_name = request.matchdict['tag_name']
    tags = request.dbsession.query(Tag)\
            .filter_by(creator=user, name=tag_name)\
            .order_by(Tag.created_at.desc())\
            .limit(limit)\
            .offset(page*limit)\
            .all()
    papers = map(lambda tag: tag.paper, tags)

    query_dict = dict(
        page_prev=max(page-1, 0),
        limit_prev=limit,
        page_next=page+1,
        limit_next=limit,
        )

    view_args = dict()
    view_args['user'] = user
    view_args['papers'] = map(lambda paper: paper_cell(request, paper), papers)
    view_args['query'] = query_dict

    return view_args

@view_config(route_name='view_user_paper_ratings', renderer='../templates/user_paper_ratings.jinja2')
def view_user_paper_ratings(request):
    user = request.context.user
    limit = min(int(request.params.get('limit', 30)), 100)
    page = int(request.params.get('page', 0))

    ratings = most_recent(UserPaperRating, request.dbsession, user, page, limit)
    papers = map(lambda x: x.paper, ratings)

    query_dict = dict(
        page_prev=max(page-1, 0),
        limit_prev=limit,
        page_next=page+1,
        limit_next=limit,
        )

    view_args = dict()
    view_args['user'] = user
    view_args['papers'] = map(lambda paper: paper_cell(request, paper), papers)
    view_args['query'] = query_dict

    return view_args
