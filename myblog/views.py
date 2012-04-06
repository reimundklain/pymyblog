# -*- coding: utf-8 -*- 
from models import RouteAbleMixin, Page, Post, Comment, PostComment, Tag, NodeTag, hash_password, User
from lib import wtformsext
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.response import Response
from pyramid.security import remember, forget, authenticated_userid
from pyramid.view import view_config, forbidden_view_config
import datetime
import json
import logging
import wtforms

log = logging.getLogger(__name__)

@view_config(route_name="home", renderer="templates/base.jinja2")
def home(request):
    return dict(
        pages=Page.all(),
        posts=Post.all(),
        logged_in=authenticated_userid(request),
        )

#===============================================================================
# LoginView
#===============================================================================
class LoginView(object):

    class Form(wtforms.Form):
        username = wtforms.TextField('Username:',
            [wtforms.validators.Length(min=3), ])
        password = wtforms.PasswordField('Password:',
            [wtforms.validators.Length(min=3), ])

    def __init__(self, request):
        self.request = request

    @view_config(route_name="login", renderer="templates/login.jinja2")
    @forbidden_view_config(renderer="templates/login.jinja2")
    def login(self):
        login_url = self.request.route_url("login")
        referrer = self.request.url
        if referrer == login_url:
            referrer = '/'  # never use the login form itself as came_from
        came_from = self.request.params.get('came_from', referrer)
        message = ''
        username = ''
        password = ''
        form = LoginView.Form(self.request.POST)
        if self.request.method == 'POST' and form.validate():
            username = form.username.data
            password = hash_password(form.password.data)
            if User.exist(username) and User.by_username(username).password == password:
                headers = remember(self.request, username)
                return HTTPFound(location=came_from, headers=headers)
            message = "Failed login"
        return dict(
            message=message,
            url=self.request.route_url('login'),
            came_from=came_from,
            form=form,
            logged_in=authenticated_userid(self.request),
            )

    @view_config(route_name="logout")
    def logout(self):
        headers = forget(self.request)
        return HTTPFound(
            location=self.request.route_url('home'),
            headers=headers
            )

#===============================================================================
# PageView
#===============================================================================
class PageView(object):
    class Form(wtforms.Form):
        title = wtforms.TextField('Title:',
            [wtforms.validators.Length(min=1, max=128), ])
        body = wtforms.TextAreaField('Body:')
        is_published = wtforms.BooleanField('Published:', default=False)
        submit = wtforms.SubmitField('Submit')

    def __init__(self, request):
        self.request = request

    @view_config(route_name="page_view", renderer="templates/page/view.jinja2")
    def view(self):
        route = self.request.matchdict['route']
        page = Page.by_route(route)
        if page is None:
            return HTTPNotFound("No such page")
        return dict(
            page=page,
            pages=Page.all(),
            logged_in=authenticated_userid(self.request),
            )

    @view_config(route_name="page_add", renderer="templates/page/edit.jinja2",
        permission='edit')
    def add(self):
        form = PageView.Form(self.request.POST)
        if self.request.method == 'POST' and form.validate():
            page = Page.add(form.title.data, form.body.data, form.is_published.data)
            return HTTPFound(
                location=self.request.route_url('page_view',
                    route=page.route)
                )
        return dict(
            url=self.request.route_url('page_add'),
            form=form,
            pages=Page.all(),
            logged_in=authenticated_userid(self.request),
            )

    @view_config(route_name="page_edit", renderer="templates/page/edit.jinja2",
        permission="edit")
    def edit(self):
        route = self.request.matchdict['route']
        page = Page.by_route(route)
        if page is None:
            return HTTPNotFound("No such page")
        form = PageView.Form(self.request.POST, page)
        if self.request.method == 'POST' and form.validate():
            page.title = form.title.data
            page.body = form.body.data
            page.is_published = form.is_published.data
            return HTTPFound(
                location=self.request.route_url('page_view',
                    route=page.route)
                )
        return dict(
            form=form,
            page=page,
            pages=Page.all(),
            logged_in=authenticated_userid(self.request),
            )

    @view_config(route_name="page_delete", permission="edit")
    def delete(self):
        route = self.request.matchdict['route']
        Page.delete(route)
        return HTTPFound(location=self.request.route_url('home'))


#===============================================================================
# BlogView
#===============================================================================
class BlogView(object):

    class Form(wtforms.Form):
        title = wtforms.TextField('Title:',
            [wtforms.validators.Length(min=1, max=128)])
        body = wtforms.TextAreaField('Body:')
        tags = wtformsext.TagField('Tags:')
        created = wtforms.DateTimeField('Creation date:',
            default=datetime.datetime.now())
        is_published = wtforms.BooleanField('Published:', default=False)

    class CommentForm(wtforms.Form):
        name = wtforms.TextField('Name:', [wtforms.validators.required(), wtforms.validators.Length(min=3, max=64), ])
        email = wtforms.TextField('E-Mail:',
            [wtforms.validators.required(), wtforms.validators.Email(), ])
        body = wtforms.TextAreaField('Message:', [wtforms.validators.required(), ])
        submit = wtforms.SubmitField('Submit:')
        parent = wtforms.HiddenField()

    def __init__(self, request):
        self.request = request

    @view_config(route_name="post_add", renderer="templates/blog/edit.jinja2", permission="edit")
    def add(self):
        form = BlogView.Form(self.request.POST)
        if self.request.method == 'POST' and form.validate():
            # create post
            post = Post.add(
                form.title.data,
                form.body.data,
                form.created.data,
                form.is_published.data
                )
            # add tags
            for tag in Tag.from_list(form.tags.data):
                nt = NodeTag()
                nt.tag = tag
                post.tags.append(nt)
            return HTTPFound(location=self.request.route_url('post_view',
                    year=post.created.strftime('%Y'),
                    month=post.created.strftime('%m'),
                    day=post.created.strftime('%d'),
                    route=RouteAbleMixin.url_quote(post.title)
                    )
                )
        return dict(
            form=form,
            url=self.request.route_url('post_add'),
            pages=Page.all(),
            logged_in=authenticated_userid(self.request),
            )

    @view_config(route_name="post_edit", renderer="templates/blog/edit.jinja2", permission='edit')
    def edit(self):
        year, month, day, route = self._get_route_args()
        post = Post.by_route(route)
        if post is None:
            return HTTPNotFound('No such post')
        form = BlogView.Form(self.request.POST, post)
        if self.request.method == 'POST' and form.validate():
            post.title = form.title.data
            post.created = form.created.data
            post.body = form.body.data
            post.is_published = form.is_published.data
            # edit tags
            del post.tags
            for tag in Tag.from_list(form.tags.data):
                nt = NodeTag()
                nt.tag = tag
                post.tags.append(nt)
            return HTTPFound(
                location=self.request.route_url('post_view',
                    year=year,
                    month=month,
                    day=day,
                    route=RouteAbleMixin.url_quote(post.title))
                )
        return dict(
            post=post,
            form=form,
            pages=Page.all(),
            logged_in=authenticated_userid(self.request),
            )

    @view_config(route_name="post_delete", permission="edit")
    def delete(self):
        year, month, day, route = self._get_route_args()
        Post.delete(route)
        return HTTPFound(
            location=self.request.route_url('home'))

    @view_config(route_name="post_view", renderer="templates/blog/view.jinja2")
    def view(self):
        year, month, day, route = self._get_route_args()
        post = Post.by_route(route)
        if post is None:
            return HTTPNotFound("No such post")
        form = BlogView.CommentForm(self.request.POST)
        if self.request.method == 'POST' and form.validate():
            if form.parent.data == '':
                post_comment = PostComment()
                post_comment.comment = Comment(form.name.data, form.email.data, form.body.data)
                post.comments.append(post_comment)
            else:
                parent_id = int(form.parent.data)
                parent_comment = Comment.by_id(parent_id)
                parent_comment.childs.append(
                    Comment(
                        form.name.data,
                        form.email.data,
                        form.body.data,
                        parent_id,
                        )
                    )
            return HTTPFound(
                location=self.request.route_url('post_view',
                    year=year,
                    month=month,
                    day=day,
                    route=RouteAbleMixin.url_quote(post.title))
                )
        return dict(
            form=form,
            post=post,
            pages=Page.all(),
            logged_in=authenticated_userid(self.request),
            )

    @view_config(route_name="post_view_y", renderer="templates/base.jinja2")
    def view_y(self):
        year = int(self.request.matchdict['year'])
        return dict(
            posts=Post.by_year(year),
            pages=Page.all(),
            logged_in=authenticated_userid(self.request),
            )

    @view_config(route_name="post_view_ym", renderer="templates/base.jinja2")
    def view_ym(self):
        year = int(self.request.matchdict['year'])
        month = int(self.request.matchdict['month'])
        return dict(
            posts=Post.by_month(year, month),
            pages=Page.all(),
            logged_in=authenticated_userid(self.request),
            )

    @view_config(route_name="post_view_ymd", renderer="templates/base.jinja2")
    def view_ymd(self):
        year = int(self.request.matchdict['year'])
        month = int(self.request.matchdict['month'])
        day = int(self.request.matchdict['day'])
        return dict(
            posts=Post.by_day(year, month, day),
            pages=Page.all(),
            logged_in=authenticated_userid(self.request),
            )

    @view_config(route_name='post_comment_delete', renderer="templates/blog/view.jinja2", permission="edit")
    def delete_comment(self):
        log.debug(self.request)
        request = self.request
        year, month, day, route = self._get_route_args()
        post = Post.by_route(route)
        if post is None:
            return HTTPNotFound('No such post')
        cid = int(request.matchdict['id'])
        comment = Comment.by_id(cid)
        post.delete_comment(comment)
        return HTTPFound(
                location=self.request.route_url('post_view',
                    year=year,
                    month=month,
                    day=day,
                    route=RouteAbleMixin.url_quote(post.title))
                )

    def _get_route_args(self):
        ''' Return tuple (year, month, day, route) '''
        year = self.request.matchdict['year']
        month = self.request.matchdict['month']
        day = self.request.matchdict['day']
        routename = self.request.matchdict['route']
        route = '%s/%s/%s/%s' % (year, month, day, routename)
        log.debug("Route: %s" % (route))
        return (year, month, day, route)


#===============================================================================
# TagView
#===============================================================================
class TagView(object):
    def __init__(self, request):
        self.request = request
        #TODO


#===============================================================================
# UserView
#===============================================================================
class UserView(object):

    class SettingsForm(wtforms.Form):
#        username = wtforms.TextField('Username:',
#            [wtforms.validators.Length(min=3), ])
        password1 = wtforms.PasswordField('Password:',
            [wtforms.validators.Length(min=3), ])
        password2 = wtforms.PasswordField('Password confirm:',
            [wtforms.validators.EqualTo('password1') ])
        submit = wtforms.SubmitField('Submit:')

    def __init__(self, request):
        self.request = request

    @view_config(route_name='user_edit', renderer='templates/user/edit.jinja2', permission="edit")
    def edit(self):
        request = self.request
        user = request.user
        if user is None:
            return HTTPNotFound('User doesn\'t exist')
        form = UserView.SettingsForm(request.POST, user)
        if request.method == 'POST' and form.validate():
            user.password = form.password1.data
        return dict(
            url=request.route_url('user_edit', id=user.id),
            form=form,
            pages=Page.all(),
            logged_in=authenticated_userid(self.request),
            )


#===============================================================================
# ImageView
#===============================================================================
class ImageView(object):

    def __init__(self, request):
        self.request = request

    @view_config(route_name='image_view', renderer='templates/image/view.jinja2')
    def view(self):
        request = self.request

        return dict()


