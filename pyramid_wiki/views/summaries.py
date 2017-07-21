from pyramid.compat import escape
import re
from docutils.core import publish_parts

from pyramid.httpexceptions import HTTPFound

from pyramid.view import view_config

@view_config(route_name='summarize', renderer='../templates/summarize.jinja2',
             permission='create')
def summarize(request):
    article_id = request.context.article_id
    if 'form.submitted' in request.params:
        raise NotImplementedError()
    save_url = request.route_url('summarize', article_id=article_id)
    return dict(
        article_id=article_id,
        save_url=save_url,
        )
