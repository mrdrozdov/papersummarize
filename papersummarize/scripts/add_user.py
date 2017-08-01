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
from ..models import User


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <username> <password> <config_uri> [var=value]' % (cmd,))
    sys.exit(1)

def main(argv=sys.argv):
    if len(argv) < 4:
        usage(argv)
    username = argv[1]
    password = argv[2]
    config_uri = argv[3]
    options = parse_vars(argv[4:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    settings.update(options)

    engine = get_engine(settings)
    Base.metadata.create_all(engine)

    session_factory = get_session_factory(engine)

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)

        user = User(name=username, role='editor')
        user.set_password(password)
        dbsession.add(user)
