from pyramid.httpexceptions import (
    HTTPNotFound,
    HTTPFound,
)
from pyramid.security import (
    Allow,
    Everyone,
)

from .models import Page, Paper, Summary

def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('view_wiki', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('view_paper', '/x/{arxiv_id}', factory=arxiv_factory)
    config.add_route('add_summary', '/x/{arxiv_id}/add_summary', factory=new_summary_factory)
    config.add_route('edit_summary', '/x/{arxiv_id}/edit_summary', factory=summary_factory)
    config.add_route('view_page', '/{pagename}', factory=page_factory)
    config.add_route('add_page', '/add_page/{pagename}',
                     factory=new_page_factory)
    config.add_route('edit_page', '/{pagename}/edit_page',
                     factory=page_factory)

def new_summary_factory(request):
    arxiv_id = request.matchdict['arxiv_id']
    paper = request.dbsession.query(Paper).filter_by(arxiv_id=arxiv_id).first()
    if paper is None:
        raise HTTPNotFound
    summary = request.dbsession.query(Summary).filter_by(paper=paper).first()
    if summary is not None:
        next_url = request.route_url('edit_summary', arxiv_id=paper.arxiv_id)
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
    paper = request.dbsession.query(Paper).filter_by(arxiv_id=arxiv_id).first()
    if paper is None:
        raise HTTPNotFound
    summary = request.dbsession.query(Summary).filter_by(paper=paper).first()
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

def arxiv_factory(request):
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
