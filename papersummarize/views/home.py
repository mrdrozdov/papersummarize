from pyramid.compat import escape
import re
from docutils.core import publish_parts

from pyramid.httpexceptions import HTTPFound, HTTPNotFound

from pyramid.view import view_config

from .helpers.paper import paper_cell
from ..shared import paper_utils
from ..models import Paper
from ..shared.url_parsing import parse_arxiv_url

@view_config(route_name='home', renderer='../templates/home.jinja2')
def home(request):
    limit = min(int(request.params.get('limit', 30)), 100)
    page = int(request.params.get('page', 0))

    query = request.dbsession.query(Paper)
    query = query.order_by(Paper.published.desc())
    query = query.limit(limit).offset(page*limit)

    papers = query.all()

    query_dict = dict(
        page_prev=max(page-1, 0),
        limit_prev=limit,
        page_next=page+1,
        limit_next=limit,
        )

    view_args = dict()
    view_args['papers'] = map(lambda paper: paper_cell(request, paper), papers)
    view_args['query'] = query_dict

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
    return view_args
