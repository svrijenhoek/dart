import json
import os
import random
import numpy as np
import dart.Util as Util


class UserSimulator:

    def __init__(self, config, handlers):
        self.handlers = handlers

        self.n_users = config["user_number"]
        self.load_users = config["user_load"]
        if self.load_users == "Y":
            self.alternative_schema = config["user_alternative_schema"]
            self.folder = config["user_folder"]
            self.schema = Util.read_json_file(config['user_schema'])
            self.user_reading_history_based_on = config["user_reading_history_based_on"]

        self.base_date = config['reading_history_date']
        self.classifications = ['politiek', 'sport', 'entertainment', 'onbekend', 'financieel']
        self.sources = ['nu', 'geenstijl', 'volkskrant (www)']
        self.parties = config["political_parties"]

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
                        if self.alternative_schema == "Y":
                            json_doc = Util.transform(json_doc, self.schema)
                            if 'reading_history' in json_doc:
                                if self.user_reading_history_based_on == "title":
                                    json_doc['reading_history'] = {'base': self.reading_history_to_ids(json_doc['reading_history'])}
                            else:
                                json_doc['reading_history'] = {'base': self.simulate_reading_history()}
                        body = json.dumps(json_doc)
                        self.handlers.users.add_user(body)
        # else:
        # simulate user data
        for _ in range(0, self.n_users):
            classification_pref = random.choice(self.classifications)
            source_pref = random.choice(self.sources)
            complexity_pref = int(np.random.normal(40, 10, 1)[0])
            party_pref = random.choice(self.parties)
            size = max(10, int(np.random.normal(50, 25, 1)[0]))
            reading_history = self.simulate_reading_history(classification_pref, source_pref, complexity_pref, size)
            json_doc = {
                "classification_preference": classification_pref,
                "source_preference": source_pref,
                "complexity_preference": complexity_pref,
                "party_preference": party_pref,
                "reading_history": {'base': reading_history}
            }
            body = json.dumps(json_doc)
            self.handlers.users.add_user(body)

