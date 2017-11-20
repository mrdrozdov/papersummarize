import sys
import json
import difflib
import transaction

from .defaults import defaults

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
from ..models import Paper, User, Tag


def main(argv=sys.argv):
    config_uri = argv[1]
    titles_path = argv[2]
    tag_name = argv[3]
    user_name = argv[4]

    flags = dict(config_uri=argv[1],
                 titles_path=argv[2],
                 tag_name=argv[3],
                 user_name=argv[4],
                 )

    print(json.dumps(flags, sort_keys=True, indent=4))

    # Read Titles
    titles = []
    with open(titles_path) as f:
        for line in f:
            titles.append(line.strip())

    options = dict()
    options.update(defaults)
    options.update(parse_vars(argv[5:]))

    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    engine = get_engine(settings)
    Base.metadata.create_all(engine)
    session_factory = get_session_factory(engine)

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)

        papers = dbsession.query(Paper).all()
        papers_by_title = list(sorted(papers, key=lambda x: x.title))
        paper_titles = sorted(map(lambda x: x.title, papers_by_title))

        for p, t in zip(papers_by_title, paper_titles):
            assert p.title == t, "sorting didn't work as expected"

        # Find most likely paper match
        found = 0
        almost = 0
        skipped = 0
        indexes = []

        for i, t in enumerate(titles):
            try:
                index = paper_titles.index(t)
                indexes.append((index, None))
                found += 1
            except:
                matches = difflib.get_close_matches(t, paper_titles, n=1, cutoff=0.9)
                if len(matches) == 0:
                    indexes.append((None, None))
                    skipped += 1
                else:
                    index = paper_titles.index(matches[0])
                    indexes.append((None, index))
                    almost += 1

        print("found={} almost={} skipped={}".format(found, almost, skipped))

        added = 0
        failed = 0

        user = dbsession.query(User).filter_by(name=user_name).first()

        for i_found, i_almost in indexes:
            try:
                if i_found is not None:
                    paper = papers_by_title[i_found]
                elif i_almost is not None:
                    paper = papers_by_title[i_almost]
                else:
                    continue
                tag = Tag(creator=user, paper=paper)
                tag.set_name(tag_name)
                dbsession.add(tag)
                added += 1
            except Exception as e:
                print(e)
                failed += 1

        print("user={} tag={} added={} failed={}".format(user_name, tag_name, added, failed))

