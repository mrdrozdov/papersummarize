from pyramid.compat import escape
import re
from docutils.core import publish_parts

from pyramid.httpexceptions import HTTPFound, HTTPNotFound

from pyramid.view import view_config

from .helpers.paper import paper_cell
from ..models import Tag, Tip, Paper, UserPaperRating
from ..shared import paper_utils
from ..shared.url_parsing import parse_arxiv_url

@view_config(route_name='view_user', renderer='../templates/user_profile.jinja2')
def view_user(request):
    user = request.context.user
    return dict(user=user)

@view_config(route_name='view_user_activity', renderer='../templates/user_activity.jinja2')
def view_user_activity(request):
    user = request.context.user
    tips = user.created_tips
    tags = user.created_tags
    user_paper_ratings = user.created_user_paper_ratings
    activities = tips + tags + user_paper_ratings
    activities = reversed(sorted(activities, key=lambda x: x.created_at))

    def create_item_from_activity(a):
        item = dict()
        item['created_at'] = a.created_at
        item['paper'] = a.paper

        if isinstance(a, Tip):
            item['type'] = 'tip'
        elif isinstance(a, Tag):
            item['type'] = 'tag'
            item['tag'] = a
        elif isinstance(a, UserPaperRating):
            item['type'] = 'user_paper_rating'
            item['rating'] = a.rating
        else:
            item['type'] = 'unknown'

        return item

    activities = map(create_item_from_activity, activities)

    return dict(user=user, activities=activities)

@view_config(route_name='view_user_taglist', renderer='../templates/user_taglist.jinja2')
def view_user_taglist(request):
    user = request.context.user
    tag_name = request.matchdict['tag_name']
    tags = request.dbsession.query(Tag).filter_by(creator=user, name=tag_name).all()
    papers = map(lambda tag: tag.paper, tags)

    view_args = dict()
    view_args['user'] = user
    view_args['papers'] = map(lambda paper: paper_cell(request, paper), papers)

    return view_args

@view_config(route_name='view_user_paper_ratings', renderer='../templates/user_paper_ratings.jinja2')
def view_user_paper_ratings(request):
    user = request.context.user
    ratings = request.dbsession.query(UserPaperRating).filter_by(creator=user).all()
    papers = map(lambda x: x.paper, ratings)

    view_args = dict()
    view_args['user'] = user
    view_args['papers'] = map(lambda paper: paper_cell(request, paper), papers)

    return view_args
