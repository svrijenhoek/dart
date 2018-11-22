import json
import Util
from Elastic.Connector import Connector
from Elastic.Search import Search

n_users = Util.read_config_file("user", "number_of_users")
n_topics = Util.read_config_file("user", "average_topical_interest")
n_spread = Util.read_config_file("user", "average_spread_per_interest")
mean_popular = Util.read_config_file("user", "size_popular_stories")
mean_random = Util.read_config_file("user", "size_random")

connector = Connector()
searcher = Search()

for x in range(0, n_users):
    # generate reading history
    reading_history = []
    # get articles around topics
    for y in range(0, n_topics):
        document = searcher.get_random_document('articles')
        spread = max(Util.get_random_number(n_spread, n_spread/2), 5)
        response = searcher.get_similar_documents('articles', document['_source']['id'], spread)
        for article in response:
            reading_history.append(article['_id'])

    # add most popular stories
    n_popular = max(1, Util.get_random_number(mean_popular, mean_popular/1.5))
    response = searcher.get_most_popular(n_popular)
    for hit in response:
        reading_history.append(hit['_id'])

    # add random articles
    n_random = Util.get_random_number(mean_random, mean_random/1.5)
    for y in range(0, n_random):
        article = searcher.get_random_document('articles')
        reading_history.append(article['_source']['id'])

    json_doc = {
        "spread": spread,
        "popular": n_popular,
        "random": n_random,
        "reading_history": reading_history
    }

    user_id = json_doc.pop('_id', None)
    body = json.dumps(json_doc)

    connector.add_document('users', user_id, 'user', body)

