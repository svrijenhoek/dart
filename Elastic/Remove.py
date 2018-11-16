from Elastic.Connector import Connector


class Remove(Connector):
    def __init__(self):
        super(Connector, self).__init__()

    def clear_index(self, index):
        self.es.indices.delete(index=index, ignore=[400, 404])

    def clear_all(self):
        self.clear_index('articles')
        self.clear_index('users')


