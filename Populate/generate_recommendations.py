from datetime import datetime, timedelta

import numpy as np
import json

import Util
from Elastic.Connector import Connector
from Elastic.Search import Search

connector = Connector()
searcher = Search()

timerange = Util.read_config_file("recommendations", "range")
size = Util.read_config_file("recommendations", "size")
dates = Util.read_config_file("recommendations", "dates")

users = searcher.get_all_documents('users')

for date in dates:
    print(date)
    upper = datetime.strptime(date, '%d-%m-%Y')
    lower = upper - timedelta(days=timerange)
    documents = searcher.get_all_in_timerange('articles', 10000, lower, upper)
    recommendation_size = min(len(documents), size)

    for user in users:
        user_id = user['_id']
        # generate random selection
        random_numbers = np.random.choice(len(documents), recommendation_size, False)
        random_recommendation = [documents[i] for i in random_numbers]
        # select most popular
        most_popular_recommendation = [documents[i] for i in range(int(recommendation_size))]
        # add recommendations to elasticsearch
        json_doc = {
            "user_id": user_id,
            "date": date,
            "random": random_recommendation,
            "most_popular": most_popular_recommendation
        }
        body = json.dumps(json_doc)
        docid = json_doc.pop('_id', None)
        connector.add_document('recommendations', docid, 'recommendation', body)

