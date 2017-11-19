from pyramid.httpexceptions import HTTPFound
from pyramid.security import (
    remember,
    forget,
    )
from pyramid.view import (
    forbidden_view_config,
    view_config,
)

from ..models import User


@view_config(route_name='login', renderer='../templates/auth.jinja2')
def login(request):
    next_url = request.params.get('next', request.referrer)
    if not next_url:
        next_url = request.route_url('home')
    login_message = ''
    register_message = ''
    login = ''
    if 'form.submitted.login' in request.params:
        login = request.params['login']
        password = request.params['password']
        user = request.dbsession.query(User).filter_by(name=login).first()
        if user is not None and user.check_password(password):
            headers = remember(request, user.id)
            return HTTPFound(location=next_url, headers=headers)
        login_message = 'Failed login'
    elif 'form.submitted.register' in request.params:
        login = request.params['login']
        password = request.params['password']
        if len(login) <= 3:
            register_message = 'Login name is too short'
        elif request.dbsession.query(User).filter_by(name=login).count() > 0:
            register_message = 'Login name already exists'
        else:
            user = User(name=login, role='editor')
            user.set_password(password)
            request.dbsession.add(user)
            request.dbsession.flush() # TODO: Dirty hack.
            headers = remember(request, user.id)
            return HTTPFound(location=next_url, headers=headers)

    return dict(
        login_message=login_message,
        register_message=register_message,
        url=request.route_url('login'),
        next_url=next_url,
        login=login,
        )

@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    next_url = request.params.get('next', request.route_url('home'))
    return HTTPFound(location=next_url, headers=headers)

@forbidden_view_config()
def forbidden_view(request):
    next_url = request.route_url('login', _query={'next': request.params.get('next', request.url)})
    return HTTPFound(location=next_url)
