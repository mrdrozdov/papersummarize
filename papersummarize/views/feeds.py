from pyramid.compat import escape
import re
from docutils.core import publish_parts

from pyramid.httpexceptions import HTTPFound, HTTPNotFound

from pyramid.view import view_config

from sqlalchemy import desc

from .helpers.paper import paper_cell
from .helpers.tip import tip_cell
from ..shared import paper_utils
from ..models import Paper, PaperRating, Tip
from ..shared.url_parsing import parse_arxiv_url

@view_config(route_name='new', renderer='../templates/home.jinja2')
def new(request):
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
    return view_args

@view_config(route_name='top', renderer='../templates/home.jinja2')
def top(request):
    limit = min(int(request.params.get('limit', 30)), 100)
    page = int(request.params.get('page', 0))

    query = request.dbsession.query(Paper)
    query = query.join(Paper.rating)
    query = query.order_by(PaperRating.value.desc())
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
    return view_args

@view_config(route_name='tips', renderer='../templates/tips.jinja2')
def tips(request):
    limit = min(int(request.params.get('limit', 30)), 100)
    page = int(request.params.get('page', 0))

    query = request.dbsession.query(Tip)
    query = query.order_by(Tip.created_at.desc())
    query = query.limit(limit).offset(page*limit)

    tips = query.all()

    query_dict = dict(
        page_prev=max(page-1, 0),
        limit_prev=limit,
        page_next=page+1,
        limit_next=limit,
        )

    view_args = dict()
    view_args['tips'] = map(lambda tip: tip_cell(request, tip), tips)
    view_args['query'] = query_dict

    return view_args
