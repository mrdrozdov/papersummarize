import os
import sys
import transaction
from datetime import datetime

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from .defaults import defaults
from ..shared import paper_utils
from ..models.meta import Base
from ..models import (
    get_engine,
    get_session_factory,
    get_tm_session,
    )
from ..models import User, Paper, PaperRating, Summary, Tag, Tip
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
    options = dict()
    options.update(defaults)
    options.update(parse_vars(argv[2:]))
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)

    engine = get_engine(settings)
    Base.metadata.create_all(engine)

    session_factory = get_session_factory(engine)

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)

        with open(settings['default.users']) as f:
            users = []
            for i, line in enumerate(f):
                line = line.strip().split(',')
                if i == 0:
                    header = line
                    continue
                u = {k: v for k, v in zip(header, line)}
                users.append(u)

        for u in users:
            new_user = User(name=u['name'], role='editor')
            new_user.set_password(u['password'])
            dbsession.add(new_user)

        print("Added {} users.".format(len(users)))
            
