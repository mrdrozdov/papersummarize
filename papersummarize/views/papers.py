from pyramid.compat import escape
import re
from docutils.core import publish_parts

from pyramid.httpexceptions import HTTPFound

from pyramid.view import view_config

from .helpers.paper import paper_cell
from ..shared import paper_utils
from ..models import Paper, PaperRating, Summary, Tag, Tip
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

    view_args = dict()
    view_args['paper'] = paper_cell(request, paper)

    # summary = request.dbsession.query(Summary).filter_by(creator=request.user, paper=paper).first()
    # has_wrote = summary is not None
    # has_been_reviewed = has_wrote and summary.review_status == ENUM_Summary_review_status['reviewed']
    # num_summaries = request.dbsession.query(Summary).filter_by(paper=paper).count()

    # if request.user is not None:
    #     # TODO: If the user has written a summary, always show it.
    #     if request.user.is_leader == ENUM_User_is_leader['True'] or has_been_reviewed:
    #         summaries = request.dbsession.query(Summary).filter_by(paper=paper).all()
    #     elif has_wrote:
    #         summaries = request.dbsession.query(Summary).filter_by(paper=paper, review_status=ENUM_Summary_review_status['reviewed']).all()
    #     else:
    #         summaries = request.dbsession.query(Summary).filter_by(paper=paper, review_status=ENUM_Summary_visibility['public']).all()
    #     tags = request.dbsession.query(Tag).filter_by(creator=request.user, paper=paper).all()
    # else:
    #     summaries = request.dbsession.query(Summary).filter_by(paper=paper, visibility=ENUM_Summary_visibility['public']).all()
    #     tags = None

    # # Tips
    # tips = request.dbsession.query(Tip).filter_by(paper=paper).all()
    # num_tips = request.dbsession.query(Tip).filter_by(paper=paper).count()

    # # Paper Ratings
    # paper_ratings = paper.created_paper_ratings
    # num_ratings = len(paper_ratings)
    # total_rating = sum(map(lambda x: x.rating, paper_ratings))

    # # Your Paper Rating
    # if request.user is not None:
    #     your_paper_rating = request.dbsession.query(PaperRating).filter_by(creator=request.user, paper=paper).first()
    #     has_rated_paper = your_paper_rating is not None
    # else:
    #     your_paper_rating = None
    #     has_rated_paper = False

    # def format_date(d):
    #     return d.strftime("%B %d, %Y")

    # def add_date(o):
    #     o.created_at_formatted = format_date(o.created_at)
    #     return o

    return view_args
    # dict(paper=paper,
    #     paper_object=paper_utils.paper_object(paper),
    #     has_wrote=has_wrote,
    #     num_summaries=num_summaries,
    #     summaries=map(add_date, summaries),
    #     tips=map(add_date, tips),
    #     num_tips=num_tips,
    #     tags=tags,
    #     total_rating=total_rating,
    #     num_ratings=num_ratings,
    #     your_paper_rating=your_paper_rating,
    #     has_rated_paper=has_rated_paper)

@view_config(route_name='view_similar_papers', renderer='../templates/view_similar_papers.jinja2')
def view_similar_papers(request):
    paper = request.context.paper

    # Tags
    if request.user is not None:
        tags = request.dbsession.query(Tag).filter_by(creator=request.user, paper=paper).all()
    else:
        tags = None

    # Paper Ratings
    paper_ratings = paper.created_paper_ratings
    num_ratings = len(paper_ratings)
    total_rating = sum(map(lambda x: x.rating, paper_ratings))

    # Your Paper Rating
    if request.user is not None:
        your_paper_rating = request.dbsession.query(PaperRating).filter_by(creator=request.user, paper=paper).first()
        has_rated_paper = your_paper_rating is not None
    else:
        your_paper_rating = None
        has_rated_paper = False

    # Similar Papers
    similar_papers = [paper_utils.stub_paper('some_id'), paper_utils.stub_paper('other_id')]

    return dict(paper=paper,
        paper_object=paper_utils.paper_object(paper),
        similar_papers=map(paper_utils.paper_object, similar_papers),
        tags=tags,
        total_rating=total_rating,
        num_ratings=num_ratings,
        your_paper_rating=your_paper_rating,
        has_rated_paper=has_rated_paper)

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
    paper = summary.paper
    return dict(paper=paper, summary=summary)

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

@view_config(route_name='add_tag', renderer='../templates/add_tag.jinja2',
             permission='create')
def add_tag(request):
    paper = request.context.paper
    user = request.user
    if 'form.submitted' in request.params:
        tag_name = request.params['body']
        tag = Tag(creator=request.user, paper=paper)
        tag.set_name(tag_name)
        request.dbsession.add(tag)
        next_url = request.route_url('view_paper', arxiv_id=paper.arxiv_id)
        return HTTPFound(location=next_url)
    tags = request.dbsession.query(Tag).filter_by(creator=user, paper=paper).all()
    save_url = request.route_url('add_tag', arxiv_id=paper.arxiv_id)
    return dict(paper=paper, save_url=save_url, tags=tags)

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
