import os
import sys
import json
from datetime import datetime
import pickle
import transaction

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from ..models.meta import Base
from ..models import (
    get_engine,
    get_session_factory,
    get_tm_session,
    )

from ..models import Paper

class ArxivPaper():
    _rawid = None
    _version = None
    arxiv_comment = None
    arxiv_primary_category = None
    author = None
    author_detail = None
    authors = None
    link = None
    links = None
    published = None
    summary = None
    tags = None
    title = None
    updated = None

    def __init__(self, raw):
        for k in raw.keys():
            setattr(self, k, raw[k])

def fmt_dt(dt):
    return datetime.strptime(dt, '%Y-%m-%dT%H:%M:%SZ')

def fmt_obj(obj):
    if obj:
        return json.dumps(obj)
    else:
        return json.dumps({})

def fmt_arxiv_id(_rawid, _version):
    return '{}v{}'.format(_rawid, _version)

def read_arxiv_paper(raw_paper):
    paper = Paper(
        _rawid=raw_paper._rawid,
        _version=raw_paper._version,
        arxiv_id=fmt_arxiv_id(raw_paper._rawid, raw_paper._version),
        arxiv_comment=raw_paper.arxiv_comment,
        arxiv_primary_category=fmt_obj(raw_paper.arxiv_primary_category),
        author=raw_paper.author,
        author_detail=fmt_obj(raw_paper.author_detail),
        authors=fmt_obj(raw_paper.authors),
        link=raw_paper.link,
        links=fmt_obj(raw_paper.links),
        published=fmt_dt(raw_paper.published),
        summary=raw_paper.summary,
        tags=fmt_obj(raw_paper.tags),
        title=raw_paper.title,
        updated=fmt_dt(raw_paper.updated),
        )
    return paper

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> <papers.pickle>' % (cmd,))
    sys.exit(1)

def main(argv=sys.argv):
    if len(argv) < 3:
        usage(argv)
    config_uri = argv[1]
    filename = argv[2]

    raw_papers = pickle.load(open(filename, 'rb'))
    papers = map(ArxivPaper, raw_papers.values())

    setup_logging(config_uri)
    settings = get_appsettings(config_uri)

    engine = get_engine(settings)
    Base.metadata.create_all(engine)

    session_factory = get_session_factory(engine)

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)

        for arxiv_paper in papers:
            paper = read_arxiv_paper(arxiv_paper)
            dbsession.add(paper)
            print(paper.arxiv_id)
