from pyramid.compat import escape
import re
from docutils.core import publish_parts

from pyramid.httpexceptions import HTTPFound, HTTPNotFound

from pyramid.view import view_config

from ..shared.url_parsing import parse_arxiv_url

@view_config(route_name='home', renderer='../templates/home.jinja2')
def home(request):
    papers_to_show = ['some_id', 'other_id']
    if 'form.submitted.view' in request.params or 'form.submitted.summarize' in request.params:
        body = request.params['body']

        # arxiv_id = parse_arxiv_url(body)['arxiv_id'] # TODO: Handle pdf or abstract url. 
        # Handle only ID as well, automatically selecting version if necessary.

        arxiv_id = body

        if 'form.submitted.view' in request.params:
            next_url = request.route_url('view_paper', arxiv_id=arxiv_id)
            return HTTPFound(location=next_url)
        elif 'form.submitted.summarize' in request.params:
            next_url = request.route_url('add_summary', arxiv_id=arxiv_id)
            return HTTPFound(location=next_url)
    return dict(papers_to_show=papers_to_show)
