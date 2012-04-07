# -*- coding: utf8 -*-

from models import DBSession, Base
from pyramid import testing
import unittest


#===============================================================================
# TestRouteAbleMixin
#===============================================================================
class TestRouteAbleMixin(unittest.TestCase):

    def test(self):
        from models import RouteAbleMixin

        r = RouteAbleMixin("Test")
        self.assertEqual("test", r.route);

        r = RouteAbleMixin("Hallo da Draußen")
        self.assertEqual(u"hallo-da-draußen", r.route);

        r = RouteAbleMixin("Hallo ich bin eine Meldung von Heute")
        self.assertEqual("hallo-ich-bin-eine-meldung-von-heute", r.route)

        r = RouteAbleMixin("/////test %!\"§$%&/()")
        self.assertEqual("test", r.route)

        r = RouteAbleMixin("Hallo #2 §§$ §%§ §%??\" Meldung von Heute  -  23423 §$\"§)")
        self.assertEqual('hallo-2-meldung-von-heute-23423', r.route)

        r = RouteAbleMixin("Test__k")
        self.assertEqual("test-k", r.route);


#===============================================================================
# TestImageModel
#===============================================================================
class TestImageModel(unittest.TestCase):


    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine
        engine = create_engine('sqlite://')
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)

    def tearDown(self):
        pass

    def test_add(self):
        from models import Image
        Image.add(name="Hallo.img")

        img = Image.by_id(1)
        self.assertEqual(1, img.id)
        self.assertEqual("Hallo.img", img.name)
        self.assertEqual("hallo.img", img.route)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
