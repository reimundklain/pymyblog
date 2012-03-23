
from models import User
from pyramid.security import unauthenticated_userid
import logging

log = logging.getLogger(__name__)
def groupfinder(username, request):
    log.debug('username: %s' % (username))
    if User.exist(username):
        user = User.by_username(username)
        return ['group:%s' % (group.group.name) for group in user.groups ]


def get_user(request):
    username = unauthenticated_userid(request)
    log.debug('userid:%s' % (username))
    if username is not None:
        return User.by_username(username)

