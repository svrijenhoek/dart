from dart.handler.elastic.base_handler import BaseHandler


class UserHandler(BaseHandler):
    def __init__(self):
        super(BaseHandler, self).__init__()

    def get_all_users(self):
        return super(UserHandler, self).get_all_documents('users')
