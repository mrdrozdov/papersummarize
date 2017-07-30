from pyramid.compat import escape
import re
from docutils.core import publish_parts

from pyramid.httpexceptions import HTTPFound

from pyramid.view import view_config

from .helpers.paper import paper_cell
from .helpers.summary import summaries_for_paper, summary_cell
from .helpers.tip import tip_cell
from ..shared import paper_utils
from ..models import Paper, PaperRating, Summary, Tag, Tip
from ..shared.enums import ENUM_User_is_leader, ENUM_Summary_visibility, ENUM_Summary_review_status

@view_config(route_name='view_paper', renderer='../templates/paper.jinja2',
             permission='view')
def view_paper(request):
    paper = request.context.paper
    summary = request.dbsession.query(Summary).filter_by(creator=request.user, paper=paper).first()
    summaries = summaries_for_paper(request, paper)
    tips = request.dbsession.query(Tip).filter_by(paper=paper).all()

    view_args = dict()
    view_args['paper'] = paper_cell(request, paper)
    view_args['summary'] = summary
    view_args['summaries'] = map(lambda summary: summary_cell(summary), summaries)
    view_args['tips'] = map(lambda tip: tip_cell(tip), tips)

    return view_args

@view_config(route_name='view_similar_papers', renderer='../templates/view_similar_papers.jinja2')
def view_similar_papers(request):
    paper = request.context.paper
    similar_papers = [paper_utils.stub_paper('some_id'), paper_utils.stub_paper('other_id')]

    view_args = dict()
    view_args['paper'] = paper_cell(request, paper)
    view_args['papers'] = map(lambda paper: paper_cell(request, paper), papers)

    return view_args

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

@view_config(route_name='view_summary', renderer='../templates/view_summary.jinja2')
def view_summary(request):
    summary = request.context.summary
    view_args = dict()
    view_args['summary'] = summary_cell(summary)
    return view_args

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

@view_config(route_name='add_tag', permission='create')
def add_tag(request):
    next_url = request.params.get('next', request.referrer)
    if not next_url:
        next_url = request.route_url('home')

    paper = request.context.paper
    user = request.user

    if not request.params.get('body', None):
        return HTTPFound(location=next_url)

    tag_name = request.params['body']
    tag = Tag(creator=request.user, paper=paper)
    tag.set_name(tag_name)
    request.dbsession.add(tag)

    return HTTPFound(location=next_url)

@view_config(route_name='delete_tag', permission='edit')
def delete_tag(request):
    next_url = request.params.get('next', request.referrer)
    if not next_url:
        next_url = request.route_url('home')
    tag = request.context.tag
    request.dbsession.delete(tag)
    return HTTPFound(location=next_url)

@view_config(route_name='add_paper_rating', permission='create')
def add_paper_rating(request):
    rating = request.matchdict['rating']
    paper = request.context.paper
    paper_rating = PaperRating(creator=request.user, paper=paper)
    paper_rating.set_rating(rating)
    request.dbsession.add(paper_rating)
    next_url = request.params.get('next', request.referrer)
    if not next_url:
        next_url = request.route_url('view_paper', arxiv_id=paper.arxiv_id)
    return HTTPFound(location=next_url)

@view_config(route_name='edit_paper_rating', permission='edit')
def edit_paper_rating(request):
    next_url = request.params.get('next', request.referrer)
    if not next_url:
        next_url = request.route_url('home')
    paper_rating = request.context.paper_rating
    rating = request.matchdict['rating']
    paper_rating.rating = rating
    return HTTPFound(location=next_url)

@view_config(route_name='delete_paper_rating', permission='edit')
def delete_paper_rating(request):
    next_url = request.params.get('next', request.referrer)
    if not next_url:
        next_url = request.route_url('home')
    paper_rating = request.context.paper_rating
    request.dbsession.delete(paper_rating)
    return HTTPFound(location=next_url)
