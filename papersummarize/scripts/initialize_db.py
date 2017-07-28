import os
import sys

from .initialize_papers import main as initialize_papers
from .initialize_userdata import main as initialize_userdata


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)

def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    initialize_papers(argv)
    initialize_userdata(argv)
