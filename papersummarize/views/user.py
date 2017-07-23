from pyramid.compat import escape
import re
from docutils.core import publish_parts

from pyramid.httpexceptions import HTTPFound, HTTPNotFound

from pyramid.view import view_config

from ..shared.url_parsing import parse_arxiv_url

@view_config(route_name='view_user', renderer='../templates/user_profile.jinja2')
def view_user(request):
    user = request.context.user
    return dict(user=user)
