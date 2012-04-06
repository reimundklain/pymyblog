#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pyramid.security import Allow, Everyone, ALL_PERMISSIONS
from sqlalchemy import ForeignKey, Column, Integer, UnicodeText, Unicode, \
    DateTime, Boolean, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.sql import exists
from sqlalchemy.sql.expression import desc, and_
from zope.sqlalchemy import ZopeTransactionExtension
import calendar
import datetime
import hashlib
import logging
import re
import werkzeug

log = logging.getLogger(__name__)

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

def hash_password(password):
    return hashlib.sha256(password).hexdigest()

#===============================================================================
# RootFactory
#===============================================================================
class RootFactory(object):
    ''' 
    TODO: - Make this adjustable by page and use DB
    '''
    __acl__ = [(Allow, Everyone, 'view'),
               (Allow, 'admin', ALL_PERMISSIONS),
               (Allow, 'group:editors', 'edit')]

    def __init__(self, request):
        pass


#===============================================================================
# RouteAbleMixin
#===============================================================================
class RouteAbleMixin(object):
    '''
    create valide route for routeable nodes like post or page
        Test -> test
        Hallo World -> hallo-world
    '''

    route = Column(Unicode(256), unique=True)
    def __init__(self, route):
        self.route = self.url_quote(route)

    @staticmethod
    def url_quote(s):
        s = re.sub("[^a-zA-Z0-9]", " ", s).strip(' -').lower() # stripe " " and "-" char 
        s = re.sub("\s", "-", s)
        s = re.sub("-+", "-", s)
        return s

    @classmethod
    def by_route(cls, route):
        '''
        Return RouteAbleMixin by route
        '''
        return DBSession.query(cls).filter_by(route=route).first()

    @classmethod
    def delete(cls, route):
        '''
        Delete routeable
        '''
        DBSession.delete(cls.by_route(route))

    @classmethod
    def all(cls, reverse=False):
        '''
        Get all routeable
        '''
        routables = DBSession.query(cls).order_by(desc(cls.id)).all()
        return routables

#===============================================================================
# User
#===============================================================================
class User(Base):
    '''
    TODO: - Make updated work
    '''
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.datetime.now())
    updated = Column(DateTime)
    is_superuser = Column(Boolean, default=False)
    username = Column(Unicode(32), unique=True)
    _password = Column('password', Unicode(128))
    name = Column(Unicode(32))
    email = Column(Unicode(64))

    groups = relationship('UserGroup')

    def __init__(self, username, password, email='', name='', is_superuser=False):
        self.username = username
        self._password = hash_password(password)
        self.email = email
        self.name = name
        self.is_superuser = is_superuser

    @classmethod
    def add(cls, username, password, email, name='', is_superuser=False):
        user = cls(username, password, email, name, is_superuser)
        DBSession.add(user)
        return user

    @classmethod
    def by_username(cls, username):
        return DBSession.query(cls).filter_by(username=username).first()

    @classmethod
    def by_id(cls, id):
        return DBSession.query(cls).filter_by(id=id).first()

    @classmethod
    def exist(cls, username):
        res = DBSession.query(cls).filter_by(username=username).first()
        if res is None:
            return False
        else:
            return True


    @property
    def password(self): return self._password
    @password.setter
    def password(self, value):
        self._password = hash_password(value)
        self.updated = datetime.datetime.now()




#===============================================================================
# UserGroup
#===============================================================================
class UserGroup(Base):
    '''
    Assoc. between user m <---> n group
    '''
    __tablename__ = 'user_groups'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id'), primary_key=True)
    group = relationship('Group')

#===============================================================================
# Group
#===============================================================================
class Group(Base):
    '''
    TODO: - Make updated work
    '''
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.datetime.now())
    updated = Column(DateTime)
    name = Column(Unicode(32))

    def __init__(self, name):
        self.name = name

    @classmethod
    def add(cls, name):
        group = cls(name)
        DBSession.add(group)
        return group

#===============================================================================
# Node
#===============================================================================
class Node(Base):
    __tablename__ = 'nodes'
    discriminator = Column('type', Unicode(64))
    __mapper_args__ = {'polymorphic_on': discriminator}

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.datetime.now())
    updated = Column(DateTime)
    is_published = Column(Boolean, default=False)

    tags = relationship('NodeTag', cascade="all, delete, delete-orphan")

#===============================================================================
# NodeTag
#===============================================================================
class NodeTag(Base):
    __tablename__ = 'node_tags'
    node_id = Column(Integer, ForeignKey('nodes.id'), primary_key=True)
    tags_id = Column(Integer, ForeignKey('tags.id'), primary_key=True)
    tag = relationship('Tag')

#    @classmethod
#    def exist(cls, node, tag):
#        if DBSession.query(cls).filter_by(node_id=node.id, tags_id=tag.id).first() is not None:
#            return False
#        return True

#===============================================================================
# Page
#===============================================================================
class Page(Node, RouteAbleMixin):
    __tablename__ = 'pages'
    __mapper_args__ = {'polymorphic_identity': 'page'}

    id = Column(Integer, ForeignKey('nodes.id'), primary_key=True)
    _title = Column('title', Unicode(256), unique=True)
    _body = Column('body', UnicodeText)

    def __init__(self, title, body="", is_published=False):
        self.title = title
        self.body = body
        self.is_published = is_published
        log.debug("Created %s" % (self))

    @classmethod
    def add(cls, title, body="", is_published=False):
        '''
        Create a new page and return 
        '''
        page = cls(title, body, is_published)
        DBSession.add(page)
        return page

    @classmethod
    def by_title(cls, title):
        '''
        Get by title
        '''
        return DBSession.query(cls).filter_by(title=title).first()

    @classmethod
    def exist(cls, title):
        '''
        Look if page exist
        '''
        res = DBSession.query(cls).filter_by(title=title).first()
        if res is None:
            return False
        else:
            return True

    # PROPERTYS
    @property
    def body(self): return self._body
    @body.setter
    def body(self, value):
        self._body = value.strip()
        self.updated = datetime.datetime.now()

    @property
    def title(self): return self._title
    @title.setter
    def title(self, value):
        self._title = value.strip()
        self.route = RouteAbleMixin.url_quote(self._title)
        self.updated = datetime.datetime.now()

    def __str__(self):
        return "Page(title=%s)" % (self.title)

#===============================================================================
# Post
#===============================================================================
class Post(Node, RouteAbleMixin):
    __tablename__ = 'posts'
    __mapper_args__ = {'polymorphic_identity': 'post'}

    id = Column(Integer, ForeignKey('nodes.id'), primary_key=True)
    _title = Column('title', Unicode(256))
    _body = Column('body', UnicodeText)
    comments = relationship('PostComment', cascade='all, delete, delete-orphan')

    def __init__(self, title, body="", created=datetime.datetime.now()):
        self.created = created
        self.title = title
        self.body = body

    def _to_route(self, title):
        ''' helper to create route with datetime for post '''
        return ('%s/%s' % (self.created.strftime('%Y/%m/%d'),
            RouteAbleMixin.url_quote(title)))

    @classmethod
    def add(cls, title, body, created, is_published):
        post = cls(title, body, created)
        post.is_published = is_published
        DBSession.add(post)
        return post

    @classmethod
    def by_year(cls, year):
        dayrange = calendar.monthrange(year, 12)[1]
        from_dt = datetime.datetime(year, 1, 1)
        to_dt = datetime.datetime(year, 12, dayrange, 23, 59, 59, 999999)
        posts = DBSession.query(cls).filter(and_(cls.created >= from_dt,
            cls.created <= to_dt)).all()
        return posts

    @classmethod
    def by_month(cls, year, month):
        dayrange = calendar.monthrange(year, month)[1]
        from_dt = datetime.datetime(year, month, 1)
        to_dt = datetime.datetime(year, month, dayrange, 23, 59, 59, 999999)
        posts = DBSession.query(cls).filter(and_(cls.created >= from_dt,
            cls.created <= to_dt)).all()
        return posts

    @classmethod
    def by_day(cls, year, month, day):
        from_dt = datetime.datetime(year, month, day)
        to_dt = datetime.datetime(year, month, day, 23, 59, 59, 999999)
        posts = DBSession.query(cls).filter(and_(cls.created >= from_dt,
            cls.created <= to_dt)).all()
        return posts

    def delete_comment(self, comment):
        '''
        get assocc obj and delte it if exist 
        '''
        # if parent_id == None then delete first postComment assoc
        if comment.parent_id == None:
            pc = DBSession.query(PostComment).filter_by(post_id=self.id, comment_id=comment.id).one()
            if comment is not None:
                self.comments.remove(pc)
        DBSession.delete(comment)

    # PROPERTYS
    @property
    def body(self): return self._body
    @body.setter
    def body(self, value):
        self._body = value
        self.updated = datetime.datetime.now()

    @property
    def title(self): return self._title
    @title.setter
    def title(self, value):
        self._title = value
        self.route = self._to_route(self._title)
        self.updated = datetime.datetime.now()

    def number_of_comments(self):
        ''' return total quantity of comments '''
        log.debug(self.comments)
        def count_rec(comment):
            count = 1
            for child in comment.childs:
                count += count_rec(child)
            return count

        number = 0
        for assoc in self.comments:
            number += count_rec(assoc.comment)
        return number


    @classmethod
    def by_id(cls, id):
        return DBSession.query(cls).get(id)



#===============================================================================
# PostComment Association
#===============================================================================
class PostComment(Base):
    __tablename__ = 'post_comments'
    post_id = Column(Integer, ForeignKey('posts.id'), primary_key=True)
    comment_id = Column(Integer, ForeignKey('comments.id'), primary_key=True)
    comment = relationship('Comment')

    @classmethod
    def by_ids(cls, post_id, comment_id):
        DBSession


#===============================================================================
# Comment
#===============================================================================
class Comment(Node):
    __tablename__ = 'comments'
    __mapper_args__ = {'polymorphic_identity': 'comment'}

    id = Column(Integer, ForeignKey('nodes.id'), primary_key=True)
    parent_id = Column(Integer, ForeignKey('comments.id'))
    email = Column(Unicode(128))
    name = Column(Unicode(64))
    body = Column(UnicodeText)
    childs = relationship('Comment', primaryjoin=parent_id == id, cascade='all, delete, delete-orphan')

    def __init__(self, name, email, body, parent_id=None, is_published=True):
        self.name = name
        self.email = email
        self.body = body
        self.is_published = is_published

    @classmethod
    def by_id(cls, id):
        return DBSession.query(cls).filter_by(id=id).first()


#===============================================================================
# Tags
#===============================================================================
class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    node_id = Column(Integer, ForeignKey('nodes.id'))
    created = Column(DateTime, default=datetime.datetime.now())
    name = Column(Unicode(32), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name.strip().lower()
        self.created = datetime.datetime.now()

    @classmethod
    def from_list(cls, tag_list):
        tags = []
        for tag in tag_list:
            if cls.exist(tag):
                tags.append(cls.by_name(tag))
            else:
                tags.append(cls.add(tag))
        return tags

    @classmethod
    def add(cls, name):
        tag = cls(name)
        DBSession.add(tag)
        return tag

    @classmethod
    def exist(cls, name):
        if DBSession.query(cls).filter_by(name=name).first() == None:
            return False
        return True

    @classmethod
    def by_name(cls, name):
        return DBSession.query(cls).filter_by(name=name).first()

    def __repr__(self):
        return '%s(%r)' % (self.__class__, self.__dict__)

#===============================================================================
# Category
#===============================================================================
class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    node_id = Column(Integer, ForeignKey('nodes.id'))
    created = Column(DateTime, default=datetime.datetime.now())
    name = Column(Unicode(32), unique=True, nullable=False)
