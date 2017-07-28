import os
import sys
import transaction
from datetime import datetime

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from ..shared import paper_utils
from ..models.meta import Base
from ..models import (
    get_engine,
    get_session_factory,
    get_tm_session,
    )
from ..models import User, Paper, Summary, Tag, Tip
from ..shared.enums import ENUM_User_is_leader
from ..shared.enums import ENUM_Summary_visibility, ENUM_Summary_review_status
from ..shared.enums import ENUM_Tip_category


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)

def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)

    engine = get_engine(settings)
    Base.metadata.create_all(engine)

    session_factory = get_session_factory(engine)

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)

        some_paper = dbsession.query(Paper).filter_by(arxiv_id=paper_utils.some_paper_id).first()
        other_paper = dbsession.query(Paper).filter_by(arxiv_id=paper_utils.other_paper_id).first()

        editor = User(name='editor', role='editor', is_leader=ENUM_User_is_leader['True'])
        editor.set_password('editor')
        dbsession.add(editor)

        basic = User(name='basic', role='basic')
        basic.set_password('basic')
        dbsession.add(basic)

        basic_users = []
        for i in range(10):
            basic_user = User(name='basic' + str(i), role='basic')
            basic_user.set_password('basic')
            dbsession.add(basic_user)
            basic_users.append(basic_user)

        summary_unaccepted = Summary(
            creator=basic_users[0],
            paper=other_paper,
            data='this summary is under review.',
            visibility=ENUM_Summary_visibility['members'],
            review_status=ENUM_Summary_review_status['under_review'],
        )
        dbsession.add(summary_unaccepted)

        summary_accepted = Summary(
            creator=basic_users[1],
            paper=other_paper,
            data='this summary is reviewed.',
            visibility=ENUM_Summary_visibility['members'],
            review_status=ENUM_Summary_review_status['reviewed'],
        )
        dbsession.add(summary_accepted)

        summary_public = Summary(
            creator=editor,
            paper=some_paper,
            data='this summary is not reviewed.',
            review_status=ENUM_Summary_review_status['under_review'],
        )
        dbsession.add(summary_public)

        summary_public = Summary(
            creator=editor,
            paper=other_paper,
            data='this summary is reviewed and public.',
            visibility=ENUM_Summary_visibility['public'],
            review_status=ENUM_Summary_review_status['reviewed'],
        )
        dbsession.add(summary_public)

        summary_public_unaccepted = Summary(
            creator=basic_users[2],
            paper=other_paper,
            data='this summary is under review and public (probably will not be possible create naturally).',
            visibility=ENUM_Summary_visibility['public'],
            review_status=ENUM_Summary_review_status['under_review'],
        )
        dbsession.add(summary_public_unaccepted)

        tip = Tip(
            creator=editor,
            paper=other_paper,
            category=ENUM_Tip_category['other'],
            data='this is a tip https://github.com/mrdrozdov/spinn',
        )
        dbsession.add(tip)

        tag_one = Tag(
            creator=editor,
            paper=other_paper,
        )
        tag_one.set_name('tag_one')
        dbsession.add(tag_one)

        tag_two = Tag(
            creator=editor,
            paper=other_paper,
        )
        tag_two.set_name('tag_two')
        dbsession.add(tag_two)
