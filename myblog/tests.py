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
        with transaction.manager:
            post = Post("Hallo World!", "Hallo body World!")
            DBSession.add(post)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()
