from datetime import datetime
import json

from ..models import Paper

some_paper_id = 'some_id'
other_paper_id = 'other_id'

def paper_object(paper):
    result = dict()
    result['arxiv_id'] = paper.arxiv_id
    result['title'] = paper.title
    result['published'] = paper.published
    result['abstract'] = paper.abstract
    result['authors'] = json.loads(paper.authors)
    return result

def stub_paper(arxiv_id):
    paper = Paper(arxiv_id=arxiv_id)
    paper._rawid = 'TODO'
    paper._version = 'TODO'
    paper.arxiv_comment = 'TODO'
    paper.arxiv_primary_category = 'TODO'
    paper.author = 'Fake Submitter'
    paper.author_detail = json.dumps({ 'name': 'fake' })
    paper.authors = json.dumps([{ 'name': 'Fake Author' }, { 'name': 'Also Fake Author' }])
    paper.link = '#'
    paper.links = 'TODO'
    paper.published = datetime.now()
    paper.abstract = 'This is an abstract.'
    paper.tags = 'TODO'
    paper.title = arxiv_id
    paper.updated = datetime.now()
    return paper