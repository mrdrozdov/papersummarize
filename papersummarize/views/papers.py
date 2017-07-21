from pyramid.compat import escape
import re
from docutils.core import publish_parts

from pyramid.httpexceptions import HTTPFound

from pyramid.view import view_config

from ..models import Paper, Summary

@view_config(route_name='view_paper', renderer='../templates/paper.jinja2',
             permission='view')
def view_paper(request):
    paper = request.context.paper
    summary_written = request.dbsession.query(Summary).filter_by(creator=request.user, paper=paper).count() == 1
    summaries_written = request.dbsession.query(Summary).filter_by(paper=paper).count()
    return dict(paper=paper, summary_written=summary_written, summaries_written=summaries_written)

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
    return dict(paper=paper, summarydata=summary.data, save_url=save_url)
