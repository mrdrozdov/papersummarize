from pyramid.compat import escape
import re
from docutils.core import publish_parts

from pyramid.httpexceptions import HTTPFound

from pyramid.view import view_config

@view_config(route_name='view_paper', renderer='../templates/paper.jinja2',
             permission='view')
def view_paper(request):
    paper = request.context.paper
    return dict(paper=paper)

@view_config(route_name='add_summary', renderer='../templates/add_summary.jinja2',
             permission='create')
def add_summary(request):
    paper = request.context.paper
    if 'form.submitted' in request.params:
        raise NotImplementedError()
    save_url = request.route_url('add_summary', arxiv_id=paper.arxiv_id)
    return dict(paper=paper, save_url=save_url)
