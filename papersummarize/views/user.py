from pyramid.compat import escape
import re
from docutils.core import publish_parts

from pyramid.httpexceptions import HTTPFound, HTTPNotFound

from pyramid.view import view_config

from ..models import Summary, Tag, Tip
from ..shared import paper_utils
from ..shared.enums import ENUM_Summary_review_status
from ..shared.url_parsing import parse_arxiv_url

@view_config(route_name='view_user', renderer='../templates/user_profile.jinja2')
def view_user(request):
    user = request.context.user
    return dict(user=user)

@view_config(route_name='view_user_activity', renderer='../templates/user_activity.jinja2')
def view_user_activity(request):
    user = request.context.user
    summaries = user.created_summaries
    # TODO: Also show any activity the current user has access to. For instance, if the session's user
    # has written a reviewed summary for a paper that the page's user has written a summary for, then
    # the page's user's summary should be visible regardless of its review status.
    if request.user != user:
        summaries = [s for s in summaries if s.review_status == ENUM_Summary_review_status['reviewed']]
    tips = user.created_tips
    tags = user.created_tags
    activities = summaries + tips + tags
    activities = reversed(sorted(activities, key=lambda x: x.created_at))

    def create_item_from_activity(a):
        if isinstance(a, Summary):
            created_at = a.reviewed_at
            if a.review_status == ENUM_Summary_review_status['reviewed']:
                text = "Created summary, which has been reviewed."
            else:
                text = "Created summary, which has not been reviewed."
            url = request.route_url('view_summary', arxiv_id=a.paper.arxiv_id, user_name=a.creator.name)
        elif isinstance(a, Tip):
            created_at = a.created_at
            text = "Created tip."
            url = request.route_url('view_tip', arxiv_id=a.paper.arxiv_id, tip_id=a.id)
        elif isinstance(a, Tag):
            created_at = a.created_at
            text = "Created tag {} for paper {}.".format(a.name, a.paper.title)
            url = request.route_url('view_paper', arxiv_id=a.paper.arxiv_id)
        else:
            created_at = a.created_at
            text = "Unknown activity."
            url = request.route_url('view_paper', arxiv_id=a.paper.arxiv_id)

        item = dict(created_at=created_at,
            text=text,
            url=url)

        return item

    activities = map(create_item_from_activity, activities)

    return dict(user=user, activities=activities)

@view_config(route_name='view_user_taglist', renderer='../templates/user_taglist.jinja2')
def view_user_taglist(request):
    user = request.context.user
    tag_name = request.matchdict['tag_name']
    tags = request.dbsession.query(Tag).filter_by(creator=user, name=tag_name).all()
    return dict(user=user, tags=tags)
