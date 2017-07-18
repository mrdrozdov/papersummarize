from pyramid.compat import escape
import re
from docutils.core import publish_parts

from pyramid.httpexceptions import HTTPFound

from pyramid.view import view_config

@view_config(route_name='summarize', renderer='../templates/summarize.jinja2')
def summarize(request):
    return dict(
        url=request.route_url('summarize'),
        )
