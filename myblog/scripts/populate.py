from ..models import DBSession, Node, Page, Post, PostComment, Comment, Tag, NodeTag, \
    Category, Base, Group, User, UserGroup 
from pyramid.paster import get_appsettings, setup_logging
from sqlalchemy import engine_from_config
import logging
import os
import pprint
import sys
import transaction

log = logging.getLogger(__name__)

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)

def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    log.debug(pprint.pprint(settings))
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        DBSession.add(User('admin', 'admin'))
        DBSession.add(Group('editors'))
