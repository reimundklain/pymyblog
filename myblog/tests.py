# -*- coding: utf-8 -*- 
from models import DBSession
from pyramid import testing
import transaction
import unittest


#from .models import DBSession

#class TestMyView(unittest.TestCase):
#    def setUp(self):
#        self.config = testing.setUp()
#        from sqlalchemy import create_engine
#        engine = create_engine('sqlite://')
#        from .models import (
#            Base,
#            MyModel,
#            )
#        DBSession.configure(bind=engine)
#        Base.metadata.create_all(engine)
#        with transaction.manager:
#            model = MyModel(name='one', value=55)
#            DBSession.add(model)
#
#    def tearDown(self):
#        DBSession.remove()
#        testing.tearDown()
#
#    def test_it(self):
#        from .views import my_view
#        request = testing.DummyRequest()
#        info = my_view(request)
#        self.assertEqual(info['one'].name, 'one')
#        self.assertEqual(info['project'], 'myblog')

#===============================================================================
# TestBlogView
#===============================================================================
class TestBlogView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine
        engine = create_engine('sqlite://')
        from models import (
            Base,
            Node,
            Post,
            Comment,
            Tag,
            NodeTag,
            )
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)


    def test_add_post(self):
        from models import Post
        with transaction.manager:
            post = Post("Hallo World!", "Hallo body World!")
            DBSession.add(post)
        post = Post.by_id(1)
        self.assertEqual(post.id, 1)
        self.assertEqual("Hallo World!", post.title)
        self.assertEqual("Hallo body World!", post.body)


#    def test_view(self):
#        from views import BlogView
#        req = testing.DummyRequest(path="/blog/2012/04/07/test")
#        print str(req)
#        view = BlogView(req)
#
#        info = view.view()
#        print info


    def tearDown(self):
        DBSession.remove()
        testing.tearDown()



#===============================================================================
# TestRouteAbleMixin
#===============================================================================
class TestRouteAbleMixin(unittest.TestCase):

    def test(self):
        from models import RouteAbleMixin

        r = RouteAbleMixin("Test")
        self.assertEqual("test", r.route);

        r = RouteAbleMixin("Hallo ich bin eine Meldung von Heute")
        self.assertEqual("hallo-ich-bin-eine-meldung-von-heute", r.route)

        r = RouteAbleMixin("/////test %!\"§$%&/()")
        self.assertEqual("test", r.route)

        r = RouteAbleMixin("Hallo #2 §§$ §%§ §%??\" Meldung von Heute  -  23423 §$\"§)")
        self.assertEqual('hallo-2-meldung-von-heute-23423', r.route)

        r = RouteAbleMixin("Test__k")
        self.assertEqual("test-k", r.route);

