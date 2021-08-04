import dart.handler.elastic.base_handler
import dart.handler.mongo.connector
import dart.models.Handlers
import pandas as pd
import pickle
import os
from pathlib import Path
import json
from datetime import datetime
import random
import csv


ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
BASE_DIR = os.path.dirname(ROOT_DIR)

elastic_connector = dart.handler.elastic.connector.ElasticsearchConnector()
mongo_connector = dart.handler.mongo.connector.MongoConnector()
handlers = dart.models.Handlers.Handlers(elastic_connector, mongo_connector)

# create articles pickle
# articles = [article['_source'] for article in handlers.articles.get_all_documents('articles')]
# df = pd.DataFrame(articles)
# file = os.path.join(BASE_DIR, Path('data/articles1.pickle'))
# with open(file, 'wb') as f:
#     pickle.dump(df, f)

# create recommendations pickle
# recommendations = []
# for recommendation_type in handlers.recommendations.get_recommendation_types():
#     per_type = [rec for rec in mongo_connector.find('recommendations', recommendation_type, {})]
#     recommendations = [*recommendations, *per_type]
# df = pd.DataFrame(recommendations)
# file = os.path.join(BASE_DIR, Path('data/recommendations.pickle'))
# with open(file, 'wb') as f:
#     pickle.dump(df, f)


# to do: add popularity
def tsv_to_pickle():
    # for JSON
    lstur = []
    file = open(os.path.join(BASE_DIR, Path('data/recommendations/lstur_pred_small.json')))
    for line in file:
        json_line = json.loads(line)
        lstur.append(json_line)
    #
    naml = []
    file = open(os.path.join(BASE_DIR, Path('data/recommendations/naml_pred_small.json')))
    for line in file:
        json_line = json.loads(line)
        naml.append(json_line)

    pop = []
    file = open(os.path.join(BASE_DIR, Path('data/recommendations/pop_pred_small.json')))
    for line in file:
        json_line = json.loads(line)
        pop.append(json_line)

    behavior_file = open(os.path.join(BASE_DIR, Path('data/recommendations/behaviors_small.tsv')))
    behaviors_csv = csv.reader(behavior_file, delimiter="\t")
    behaviors = []
    for line in behaviors_csv:
        behaviors.append(line)

    data = []
    for (a, b, c, d) in zip(behaviors, lstur, naml, pop):
        impression_index = a[0]
        userid = a[1]
        date = datetime.strptime(a[2], "%m/%d/%Y %I:%M:%S %p")
        items = a[4].strip().split(" ")
        lstur_row = b['pred_rank']
        naml_row = c['pred_rank']
        pop_row = d['pred_rank']
        lstur_list = []
        naml_list = []
        pop_list = []
        random_list = []
        for x in range(1, min(9, len(items) + 1)):
            try:
                lstur_list.append(items[lstur_row.index(x)].split("-")[0])
                naml_list.append(items[naml_row.index(x)].split("-")[0])
                pop_list.append(items[pop_row.index(x)].split("-")[0])
                random_index = random.randint(0, len(items))
                random_list.append(items[random_index].split("-")[0])
            except IndexError:
                pass
        data.append({'impr_index': impression_index, 'userid': userid, 'type': 'lstur', 'date': date, 'articles': lstur_list})
        data.append({'impr_index': impression_index, 'userid': userid, 'type': 'naml', 'date': date, 'articles': naml_list})
        data.append({'impr_index': impression_index, 'userid': userid, 'type': 'pop', 'date': date, 'articles': pop_list})
        data.append({'impr_index': impression_index, 'userid': userid, 'type': 'random', 'date': date,
                                     'articles': random_list})
    df = pd.DataFrame(data)
    file = os.path.join(BASE_DIR, Path('data/recommendations.pickle'))
    with open(file, 'wb') as f:
        pickle.dump(df, f)


tsv_to_pickle()
