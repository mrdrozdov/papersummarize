from pyramid.compat import escape
import re
from docutils.core import publish_parts

from pyramid.httpexceptions import HTTPFound

from pyramid.view import view_config

from ..models import Paper, Summary, Tip
from ..shared.enums import ENUM_User_is_leader, ENUM_Summary_visibility, ENUM_Summary_review_status

@view_config(route_name='view_paper', renderer='../templates/paper.jinja2',
             permission='view')
def view_paper(request):
    """
    Summary {
        visibility: public | members,
        review_status: reviewed | under_review,
    }

    Constraints:
        - in order to be public, the summary must be reviewed (not all reviewed summaries are public)

    Different Levels of "Visibility"

    - Public: Everyone can see it. { visibility=public, review_status=reviewed }
    - Members+Reviewed: People that have written a summary (for this paper) can see it. { visibility=members, review_status=under_review }
    - Members+UnderReview: People that have written a summary (for this paper) can see it, only if their summary has been reviewed. { visibility=members, review_status=under_review }

    """
    paper = request.context.paper
    summary = request.dbsession.query(Summary).filter_by(creator=request.user, paper=paper).first()
    has_wrote = summary is not None
    has_been_reviewed = has_wrote and summary.review_status == ENUM_Summary_review_status['reviewed']
    num_summaries = request.dbsession.query(Summary).filter_by(paper=paper).count()

    if request.user is not None:
        # TODO: If the user has written a summary, always show it.
        if request.user.is_leader == ENUM_User_is_leader['True'] or has_been_reviewed:
            summaries = request.dbsession.query(Summary).filter_by(paper=paper).all()
        elif has_wrote:
            summaries = request.dbsession.query(Summary).filter_by(paper=paper, review_status=ENUM_Summary_review_status['reviewed']).all()
        else:
            summaries = request.dbsession.query(Summary).filter_by(paper=paper, review_status=ENUM_Summary_visibility['public']).all()
    else:
        summaries = request.dbsession.query(Summary).filter_by(paper=paper, visibility=ENUM_Summary_visibility['public']).all()
    tips = request.dbsession.query(Tip).filter_by(paper=paper).all()
    num_tips = request.dbsession.query(Tip).filter_by(paper=paper).count()

    def format_date(d):
        return d.strftime("%B %d, %Y")

    def add_date(o):
        o.created_at_formatted = format_date(o.created_at)
        return o

    return dict(paper=paper,
        has_wrote=has_wrote,
        num_summaries=num_summaries,
        summaries=map(add_date, summaries),
        tips=map(add_date, tips),
        num_tips=num_tips)

@view_config(route_name='add_summary', renderer='../templates/add_summary.jinja2',
             permission='create')
def add_summary(request):
    paper = request.context.paper
    if 'form.submitted' in request.params:
        body = request.params['body']
        summary = Summary(creator=request.user, paper=paper, data=body)
        request.dbsession.add(summary)
        next_url = request.route_url('view_paper', arxiv_id=paper.arxiv_id)
        return HTTPFound(location=next_url)
    save_url = request.route_url('add_summary', arxiv_id=paper.arxiv_id)
    return dict(paper=paper, save_url=save_url)

@view_config(route_name='edit_summary', renderer='../templates/edit_summary.jinja2',
             permission='edit')
def edit_summary(request):
    summary = request.context.summary
    paper = summary.paper
    if 'form.submitted' in request.params:
        summary.data = request.params['body']
        next_url = request.route_url('view_paper', arxiv_id=paper.arxiv_id)
        return HTTPFound(location=next_url)
    save_url = request.route_url('edit_summary', arxiv_id=paper.arxiv_id)
    return dict(paper=paper, data=summary.data, save_url=save_url)

@view_config(route_name='add_tip', renderer='../templates/add_tip.jinja2',
             permission='create')
def add_tip(request):
    paper = request.context.paper
    if 'form.submitted' in request.params:
        body = request.params['body']
        tip = Tip(creator=request.user, paper=paper, data=body)
        request.dbsession.add(tip)
        next_url = request.route_url('view_paper', arxiv_id=paper.arxiv_id)
        return HTTPFound(location=next_url)
    save_url = request.route_url('add_tip', arxiv_id=paper.arxiv_id)
    return dict(paper=paper, save_url=save_url)

@view_config(route_name='view_tip', renderer='../templates/view_tip.jinja2')
def view_tip(request):
    tip = request.context.tip
    paper = tip.paper
    remove_url = request.route_url('delete_tip', arxiv_id=paper.arxiv_id, tip_id=tip.id)
    return dict(tip=tip, paper=paper, remove_url=remove_url)

@view_config(route_name='delete_tip', permission='edit')
def delete_tip(request):
    tip = request.context.tip
    paper = tip.paper
    arxiv_id = paper.arxiv_id
    request.dbsession.delete(tip)
    next_url = request.route_url('view_paper', arxiv_id=arxiv_id)
    return HTTPFound(location=next_url)
