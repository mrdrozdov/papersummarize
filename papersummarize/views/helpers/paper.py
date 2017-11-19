import json

from ...models import UserPaperRating, Tag, Tip


def tipscore(request, paper):
    return request.dbsession.query(Tip).filter_by(paper=paper).count()


def userscore(request, paper):
    if request.user:
        user_paper_rating = request.dbsession.query(UserPaperRating).filter_by(creator=request.user, paper=paper).first()
        if user_paper_rating:
            return user_paper_rating.rating
        else:
            return None
    else:
        return None


def paper_for_paper_cell(paper):
    result = dict()
    result['_paper'] = paper
    result['arxiv_id'] = paper.arxiv_id
    result['title'] = paper.title
    result['formatted_date'] = paper.published.strftime("%B %d, %Y")
    result['authors'] = json.loads(paper.authors)
    return result


def tags_for_paper_cell(request, paper):
    if request.user:
        return request.dbsession.query(Tag).filter_by(creator=request.user, paper=paper).all()
    else:
        return []


def paper_cell(request, paper):
    """ Returns dict with necessary information to populate a paper_cell view.

    PaperCell {
        paper: { title, authors, created_at },
        macroscore: int,
        summaryscore: int,
        tipscore: int,
        userscore: int or None,
        tags: [name]
    }
    """

    args = paper_for_paper_cell(paper)
    args['macroscore'] = round(paper.rating[0].value, 3)
    args['tipscore'] = tipscore(request, paper)
    args['userscore'] = userscore(request, paper)
    args['tags'] = tags_for_paper_cell(request, paper)

    return args
