from elasticsearch import Elasticsearch
from Elastic.Connector import Connector
from Elastic.Search import Search

es = Elasticsearch()
connector = Connector()
searcher = Search()

document = searcher.get_random_document('termvectors')
docid = document['_id']

termvector = connector.get_term_vector('termvectors', '_doc', docid)
print(termvector)

# for hit in response:
#     termvector = connector.get_term_vector('termvectors', 'text', hit.id)
#     print(termvector)
