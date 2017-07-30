from ...models import Summary
from ...shared.enums import ENUM_Summary_visibility, ENUM_Summary_review_status


def summary_cell(summary):
    result = dict()
    result['_summary'] = summary
    result['formatted_date'] = summary.created_at.strftime("%B %d, %Y")
    return result

def summaries_for_paper(request, paper):
    if request.user is not None:
        user_summary = request.dbsession.query(Summary).filter_by(creator=request.user, paper=paper).first()
        if user_summary is not None:
            summaries = request.dbsession.query(Summary).filter_by(paper=paper, review_status=ENUM_Summary_review_status['reviewed']).all()

            # Add user summary if it doesn't exist.
            user_summary_exists = False
            for summary in summaries:
                if request.user == summary.creator:
                    user_summary_exists = True
                    break
            if not user_summary_exists:
                summaries.insert(0, user_summary)
        else:
            summaries = request.dbsession.query(Summary).filter_by(paper=paper, review_status=ENUM_Summary_visibility['public']).all()
    else:
        summaries = request.dbsession.query(Summary).filter_by(paper=paper, visibility=ENUM_Summary_visibility['public']).all()
    return summaries
