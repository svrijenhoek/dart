from pymongo import MongoClient


class Connector:

    def __init__(self):
        self.mongo = MongoClient()
        self.client = self.mongo.client.client
