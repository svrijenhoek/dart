import json
import os
import random
import numpy as np
import pandas as pd
import dart.Util as Util


class UserSimulator:

    def __init__(self, config, handlers):
        self.handlers = handlers
        self.n_users = config["user_number"]
        self.load_users = config["user_load"]

        if self.load_users == "Y":
            self.alternative_schema = config["user_alternative_schema"]
            self.folder = config["user_folder"]
            if self.alternative_schema == "Y":
                self.schema = Util.read_json_file(config['user_schema'])
            self.user_reading_history_based_on = config["user_reading_history_based_on"]

        self.base_date = config['reading_history_date']
        self.classifications = ['political', 'sport', 'entertainment', 'unknown', 'business', 'general']
        self.sources = ['nu', 'geenstijl', 'volkskrant (www)']
        self.parties = self.extract_parties(config["politics_file"])

        self.queue = []

    def extract_parties(self, politics_file):
        df = pd.read_csv(politics_file)
        parties = df.group.unique()
        return parties

    def simulate_reading_history(self, classification, source, complexity, size):
        # generate reading history
        history = self.handlers.articles.simulate_reading_history(self.base_date, classification, source,
                                                                  complexity, size)
        return [article.id for article in history]

    def reading_history_to_ids(self, titles):
        ids = []
        for title in titles:
            article = self.handlers.articles.get_field_with_value('title', title)[0]
            ids.append(article.id)
        return ids

    def execute(self):
        if self.load_users == "Y":
            for path, _, files in os.walk(self.folder):
                for name in files:
                    # assumes all files are json-l, change this to something more robust!
                    for line in open((os.path.join(path, name))):
                        json_doc = json.loads(line)
                        json_doc['_id'] = json_doc['id']
                        if self.alternative_schema == "Y":
                            json_doc = Util.transform(json_doc, self.schema)
                        if json_doc['reading_history']:
                            if self.user_reading_history_based_on == "title":
                                json_doc['reading_history'] = \
                                    {'base': self.reading_history_to_ids(json_doc['reading_history'])}
                            # please fix this issue at a later time
                            # else:
                            #    json_doc['reading_history'] = {'base': self.simulate_reading_history()}
                        else:
                            json_doc['reading_history'] = {'base': []}
                        self.handlers.users.add_user(json_doc)
            #         if len(self.queue) > 1000:
            #             self.handlers.users.add_bulk(self.queue)
            #             self.queue = []
            # if self.queue:
            #     self.handlers.users.add_bulk(self.queue)
            #     self.queue = []
        else:
            # simulate user data
            for _ in range(0, self.n_users):
                classification_pref = random.choice(self.classifications)  # nosec
                source_pref = random.choice(self.sources)  # nosec
                complexity_pref = int(np.random.normal(40, 10, 1)[0])
                party_pref = random.choice(self.parties)  # nosec
                size = max(10, int(np.random.normal(50, 25, 1)[0]))
                reading_history = self.simulate_reading_history(classification_pref, source_pref, complexity_pref, size)
                json_doc = {
                    "classification_preference": classification_pref,
                    "source_preference": source_pref,
                    "complexity_preference": complexity_pref,
                    "party_preference": party_pref,
                    "reading_history": {'base': reading_history}
                }
                self.handlers.users.add_user(json_doc)

    def execute_tsv(self, file_location):
        tsv_file = open(file_location, encoding="utf-8")
        df = pd.read_table(tsv_file, names=["id", "userid", "timestamp", "reading_history", "interactions"])
        userids = df.userid.unique()
        for userid in userids:
            user_sessions = df[df.userid == userid]
            reading_history = user_sessions.iloc[0].reading_history
            interactions = {}
            for _, row in user_sessions.iterrows():
                interactions[row.timestamp] = row.interactions
            json_doc = {
                'userid': userid,
                'reading_history': reading_history,
                'interactions': interactions
            }
            self.handlers.users.add_user(json_doc)

