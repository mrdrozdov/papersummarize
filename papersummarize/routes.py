from pyramid.httpexceptions import (
    HTTPNotFound,
    HTTPFound,
)
from pyramid.security import (
    Allow,
    Everyone,
)

from .models import Page, Paper, PaperRating, Summary, Tag, Tip, User

def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    # Paper
    config.add_route('view_paper', '/x/{arxiv_id}', factory=paper_factory)
    config.add_route('view_similar_papers', '/x/{arxiv_id}/similar', factory=paper_factory)
    config.add_route('add_summary', '/x/{arxiv_id}/create_summary', factory=new_summary_factory)
    config.add_route('view_summary', '/x/{arxiv_id}/{user_name}', factory=summary_factory)
    config.add_route('add_tip', '/x/{arxiv_id}/tips/create', factory=new_tip_factory)
    config.add_route('view_tip', '/x/{arxiv_id}/tips/{tip_id}', factory=tip_factory)
    config.add_route('delete_tip', '/x/{arxiv_id}/tips/{tip_id}/delete', factory=tip_factory)
    config.add_route('add_tag', '/x/{arxiv_id}/tags/create', factory=new_tag_factory)
    config.add_route('delete_tag', '/x/{arxiv_id}/tags/{tag_name}/delete', factory=tag_factory)
    config.add_route('add_paper_rating', '/x/{arxiv_id}/ratings/create/{rating}', factory=new_paper_rating_factory)
    config.add_route('delete_paper_rating', '/x/{arxiv_id}/ratings/delete', factory=paper_rating_factory)
    # User
    config.add_route('view_user', '/u/{user_name}', factory=user_factory)
    config.add_route('view_user_activity', '/u/{user_name}/activity', factory=user_factory)
    config.add_route('view_user_paper_ratings', '/u/{user_name}/ratings', factory=user_factory)
    config.add_route('view_user_taglist', '/t/{user_name}/{tag_name}', factory=user_factory)
    # Page
    config.add_route('view_page', '/{pagename}', factory=page_factory)
    config.add_route('add_page', '/add_page/{pagename}',
                     factory=new_page_factory)
    config.add_route('edit_page', '/{pagename}/edit_page',
                     factory=page_factory)

def new_tip_factory(request):
    arxiv_id = request.matchdict['arxiv_id']
    paper = request.dbsession.query(Paper).filter_by(arxiv_id=arxiv_id).first()
    if paper is None:
        raise HTTPNotFound
    return NewTip(paper)

class NewTip(object):
    def __init__(self, paper):
        self.paper = paper

    def __acl__(self):
        return [
            (Allow, 'role:editor', 'create'),
            (Allow, 'role:basic', 'create'),
        ]

def new_tag_factory(request):
    arxiv_id = request.matchdict['arxiv_id']
    paper = request.dbsession.query(Paper).filter_by(arxiv_id=arxiv_id).first()
    if paper is None:
        raise HTTPNotFound
    return NewTag(paper)

class NewTag(object):
    def __init__(self, paper):
        self.paper = paper

    def __acl__(self):
        return [
            (Allow, 'role:editor', 'create'),
            (Allow, 'role:basic', 'create'),
        ]

def tag_factory(request):
    arxiv_id = request.matchdict['arxiv_id']
    tag_name = request.matchdict['tag_name']
    paper = request.dbsession.query(Paper).filter_by(arxiv_id=arxiv_id).first()
    if paper is None:
        raise HTTPNotFound
    tag = request.dbsession.query(Tag).filter_by(name=tag_name, paper=paper).first()
    if tag is None:
        raise HTTPNotFound
    return TagResource(tag)

class TagResource(object):
    def __init__(self, tag):
        self.tag = tag

    def __acl__(self):
        return [
            (Allow, Everyone, 'view'),
            (Allow, 'role:editor', 'edit'),
            (Allow, str(self.tag.creator_id), 'edit'),
        ]

def new_paper_rating_factory(request):
    arxiv_id = request.matchdict['arxiv_id']
    paper = request.dbsession.query(Paper).filter_by(arxiv_id=arxiv_id).first()
    if paper is None:
        raise HTTPNotFound
    return NewTag(paper)

class NewPaperRating(object):
    def __init__(self, paper):
        self.paper = paper

    def __acl__(self):
        return [
            (Allow, 'role:editor', 'create'),
            (Allow, 'role:basic', 'create'),
        ]

def paper_rating_factory(request):
    arxiv_id = request.matchdict['arxiv_id']
    paper = request.dbsession.query(Paper).filter_by(arxiv_id=arxiv_id).first()
    if paper is None:
        raise HTTPNotFound
    rating = request.dbsession.query(PaperRating).filter_by(creator=request.user, paper=paper).first()
    if rating is None:
        raise HTTPNotFound
    return PaperRatingResource(rating)

class PaperRatingResource(object):
    def __init__(self, paper_rating):
        self.paper_rating = paper_rating

    def __acl__(self):
        return [
            (Allow, Everyone, 'view'),
            (Allow, 'role:editor', 'edit'),
            (Allow, str(self.paper_rating.creator_id), 'edit'),
        ]

def tip_factory(request):
    arxiv_id = request.matchdict['arxiv_id']
    tip_id = request.matchdict['tip_id']
    paper = request.dbsession.query(Paper).filter_by(arxiv_id=arxiv_id).first()
    if paper is None:
        raise HTTPNotFound
    tip = request.dbsession.query(Tip).filter_by(id=tip_id, paper=paper).first()
    if tip is None:
        raise HTTPNotFound
    return TipResource(tip)

class TipResource(object):
    def __init__(self, tip):
        self.tip = tip

    def __acl__(self):
        return [
            (Allow, Everyone, 'view'),
            (Allow, 'role:editor', 'edit'),
            (Allow, str(self.tip.creator_id), 'edit'),
        ]

def new_summary_factory(request):
    arxiv_id = request.matchdict['arxiv_id']
    paper = request.dbsession.query(Paper).filter_by(arxiv_id=arxiv_id).first()
    if paper is None:
        raise HTTPNotFound
    summary = request.dbsession.query(Summary).filter_by(creator=request.user, paper=paper).first()
    if summary is not None:
        next_url = request.route_url('view_summary', arxiv_id=paper.arxiv_id, user_name=request.user.name)
        raise HTTPFound(location=next_url)
    return NewSummary(paper)

class NewSummary(object):
    def __init__(self, paper):
        self.paper = paper

    def __acl__(self):
        return [
            (Allow, 'role:editor', 'create'),
            (Allow, 'role:basic', 'create'),
        ]

def summary_factory(request):
    arxiv_id = request.matchdict['arxiv_id']
    user_name = request.matchdict['user_name']
    paper = request.dbsession.query(Paper).filter_by(arxiv_id=arxiv_id).first()
    if paper is None:
        raise HTTPNotFound
    user = request.dbsession.query(User).filter_by(name=user_name).first()
    if user is None:
        raise HTTPNotFound
    summary = request.dbsession.query(Summary).filter_by(creator=user, paper=paper).first()
    if summary is None:
        raise HTTPNotFound
    return SummaryResource(summary)

class SummaryResource(object):
    def __init__(self, summary):
        self.summary = summary

    def __acl__(self):
        return [
            (Allow, Everyone, 'view'),
            (Allow, 'role:editor', 'edit'),
            (Allow, str(self.summary.creator_id), 'edit'),
        ]

def new_page_factory(request):
    pagename = request.matchdict['pagename']
    if request.dbsession.query(Page).filter_by(name=pagename).count() > 0:
        next_url = request.route_url('edit_page', pagename=pagename)
        raise HTTPFound(location=next_url)
    return NewPage(pagename)

class NewPage(object):
    def __init__(self, pagename):
        self.pagename = pagename

    def __acl__(self):
        return [
            (Allow, 'role:editor', 'create'),
            (Allow, 'role:basic', 'create'),
        ]

def page_factory(request):
    pagename = request.matchdict['pagename']
    page = request.dbsession.query(Page).filter_by(name=pagename).first()
    if page is None:
        raise HTTPNotFound
    return PageResource(page)

class PageResource(object):
    def __init__(self, page):
        self.page = page

    def __acl__(self):
        return [
            (Allow, Everyone, 'view'),
            (Allow, 'role:editor', 'edit'),
            (Allow, str(self.page.creator_id), 'edit'),
        ]

def paper_factory(request):
    arxiv_id = request.matchdict['arxiv_id']
    paper = request.dbsession.query(Paper).filter_by(arxiv_id=arxiv_id).first()
    if paper is None:
        raise HTTPNotFound
    return PaperResource(paper)

class PaperResource(object):
    def __init__(self, paper):
        self.paper = paper

    def __acl__(self):
        return [
            (Allow, Everyone, 'view'),
        ]

def user_factory(request):
    user_name = request.matchdict['user_name']
    user = request.dbsession.query(User).filter_by(name=user_name).first()
    if user is None:
        raise HTTPNotFound
    return UserResource(user)

class UserResource(object):
    def __init__(self, user):
        self.user = user

    def __acl__(self):
        return [
            (Allow, Everyone, 'view'),
        ]
