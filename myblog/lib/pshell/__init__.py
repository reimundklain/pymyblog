# -*- coding: utf-8 -*-
from webtest import TestApp

def setup(env):
    env['request'].host = 'localhost'
    env['port'].port = 6543
    env['request'].scheme = 'https'
    env['testapp'] = TestApp(env['app'])
