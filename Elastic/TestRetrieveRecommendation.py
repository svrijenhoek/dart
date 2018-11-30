from elasticsearch import Elasticsearch

from Elastic.Search import Search

es = Elasticsearch()

searcher = Search()

most_popular = searcher.get_most_popular(10)
print(most_popular)



