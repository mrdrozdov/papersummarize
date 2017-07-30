from ...models import Summary
from ...shared.enums import ENUM_Summary_visibility, ENUM_Summary_review_status


def summary_cell(summary):
    result = dict()
    result['_summary'] = summary
    result['formatted_date'] = summary.created_at.strftime("%B %d, %Y")
    return result

def summaries_for_paper(request, paper):
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
