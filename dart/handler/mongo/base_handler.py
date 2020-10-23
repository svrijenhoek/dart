class BaseHandler:

    def __init__(self, connector):
        self.client = connector.client

    def find_one(self, database, collection, field, value):
        return self.client[database][collection].find_one({field: value})

    def find(self, database, collection, field, value):
        return self.client[database][collection].find({field: value})

    def insert_one(self, database, collection, data):
        self.client[database][collection].insert_one(data)

    def delete(self, database, collection, data):
        self.client[database][collection].remove(data)
