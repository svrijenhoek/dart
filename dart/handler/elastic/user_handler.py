from dart.handler.elastic.base_handler import BaseHandler
from dart.models.User import User


class UserHandler(BaseHandler):
    def __init__(self, connector):
        super(UserHandler, self).__init__(connector)
        self.all_users = None
        self.queue = []

    def add_user(self, doc):
        self.connector.add_document('users', '_doc', doc)

    def get_all_users(self):
        if self.all_users is None:
            self.all_users = [User(i) for i in super(UserHandler, self).get_all_documents('users')]
        return self.all_users

    def get_by_id(self, docid):
        return User(super(UserHandler, self).get_by_docid('users', docid))

    def update_user(self, user):
        doc = {'reading_history': user.reading_history}
        body = {
            "doc": doc
        }
        self.connector.update_document('users', '_doc', user.id, body)

    def update_reading_history(self, user, article_ids, recommendation_type):
        if recommendation_type in user.reading_history:
            user.reading_history[recommendation_type] = user.reading_history[recommendation_type] + article_ids
        else:
            user.reading_history[recommendation_type] = article_ids
        return user

