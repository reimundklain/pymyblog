# -*- coding: utf-8 -*- 
from models import DBSession
from security import groupfinder
from lib.jinja2filterext import markup
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from security import get_user
from sqlalchemy import engine_from_config


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    authn_policy = AuthTktAuthenticationPolicy('rklain', callback=groupfinder)
    authz_policy = ACLAuthorizationPolicy()
    config = Configurator(settings=settings, root_factory='myblog.models.RootFactory')
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.set_request_property(get_user, 'user', reify=True)
    # routes/views
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('files', 'files', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    #User
    #config.add_route('user_add', 'user/add')
    config.add_route('user_edit', 'user/{id}/edit')
    #config.add_route('user_delete', 'user/{id}/delete')

    # Page
    config.add_route('page_add', '/page/add')
    config.add_route('page_view', '/page/{route}')
    config.add_route('page_edit', '/page/{route}/edit')
    config.add_route('page_delete', '/page/{route}/delete')

    # Blog
    config.add_route('post_add', '/blog/add')
    config.add_route('post_view_y', '/blog/{year}')
    config.add_route('post_view_ym', '/blog/{year}/{month}')
    config.add_route('post_view_ymd', '/blog/{year}/{month}/{day}')
    config.add_route('post_view', '/blog/{year}/{month}/{day}/{route}')
    config.add_route('post_edit', '/blog/{year}/{month}/{day}/{route}/edit')
    config.add_route('post_delete', '/blog/{year}/{month}/{day}/{route}/delete')
    config.add_route('post_comment_delete', '/blog/{year}/{month}/{day}/{route}/comment/{id}/delete')

    # Image
    config.add_route('image_add', '/image/add')
    config.add_route('image_view', '/image/{id}')
#    config.add_route('image_edit', '/image/{route}/edit')
#    config.add_route('image_delete', '/image/{route}/delete')

    config.scan()

    #jinja2
    config.include('pyramid_jinja2')
    #config.get_jinja2_environment().filters['rst2htmlbody'] = rst2htmlbody
    config.get_jinja2_environment().filters['markdown'] = markup

    return config.make_wsgi_app()
