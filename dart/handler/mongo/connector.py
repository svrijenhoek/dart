from pymongo import MongoClient


class MongoConnector:

    def __init__(self):
        self.mongo = MongoClient()
        self.client = self.mongo.client.client

    def find_one(self, database, collection, field, value):
        return self.client[database][collection].find_one({field: value})

    def find(self, database, collection, field, value):
        return self.client[database][collection].find({field: value})

    def find(self, database, collection, query):
        return self.client[database][collection].find(query)

    def insert_one(self, database, collection, data):
        self.client[database][collection].insert_one(data)

    def delete(self, database, collection, data):
        self.client[database][collection].remove(data)

    def count(self, database, collection):
        return self.client[database][collection].count()

    def get_at_number(self, database, collection, number):
        return self.client[database][collection].find().limit(-1).skip(number).next()
