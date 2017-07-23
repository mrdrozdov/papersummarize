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
    paper = request.context.paper
    summary_written = request.dbsession.query(Summary).filter_by(creator=request.user, paper=paper).count() == 1
    num_summaries = request.dbsession.query(Summary).filter_by(paper=paper).count()

    if request.user is not None:
        # TODO: If the user has written a summary, always show it.
        if request.user.is_leader == ENUM_User_is_leader['True'] or summary_written:
            summaries = request.dbsession.query(Summary).filter_by(paper=paper).all()
        else:
            summaries = request.dbsession.query(Summary).filter_by(paper=paper, visibility=ENUM_Summary_review_status['reviewed']).all()
    else:
        summaries = request.dbsession.query(Summary).filter_by(paper=paper, visibility=ENUM_Summary_visibility['public']).all()
    tips = request.dbsession.query(Tip).filter_by(paper=paper).all()
    num_tips = request.dbsession.query(Tip).filter_by(paper=paper).count()

    return dict(paper=paper,
        summary_written=summary_written,
        num_summaries=num_summaries,
        summaries=summaries,
        tips=tips,
        num_tips=num_tips)

@view_config(route_name='add_summary', renderer='../templates/add_summary.jinja2',
             permission='create')
def add_summary(request):
    paper = request.context.paper
    if 'form.submitted' in request.params:
        body = request.params['body']
        summary = Summary(creator=request.user, paper=paper, data=body)
        request.dbsession.add(summary)
        next_url = request.route_url('edit_summary', arxiv_id=paper.arxiv_id)
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
        next_url = request.route_url('edit_summary', arxiv_id=paper.arxiv_id)
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

@view_config(route_name='edit_tip', renderer='../templates/edit_tip.jinja2',
             permission='edit')
def edit_tip(request):
    tip = request.context.tip
    paper = tip.paper
    if 'form.submitted' in request.params:
        tip.data = request.params['body']
        next_url = request.route_url('edit_tip', arxiv_id=paper.arxiv_id, tip_id=tip.id)
        return HTTPFound(location=next_url)
    save_url = request.route_url('edit_tip', arxiv_id=paper.arxiv_id, tip_id=tip.id)
    return dict(paper=paper, data=tip.data, save_url=save_url)
