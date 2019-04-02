from dart.handler.elastic.base_handler import BaseHandler
from dart.models.User import User


class UserHandler(BaseHandler):
    def __init__(self, connector):
        super(UserHandler, self).__init__(connector)
        self.all_users = None

    def get_all_users(self):
        if self.all_users is None:
            self.all_users = [User(i) for i in super(UserHandler, self).get_all_documents('users')]
        return self.all_users
