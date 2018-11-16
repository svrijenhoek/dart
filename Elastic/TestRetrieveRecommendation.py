from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

es = Elasticsearch()

client = Elasticsearch(host="localhost")

s = Search(using=client, index="recommendations") \
    .query("match", text="VVD")

response = s.execute()

print("Got %d Hits:" % response['hits']['total'])
for hit in response:
    print(hit.meta.score, hit.title)
    mlts = es.search(index='articles', body={'query': {"more_like_this": {
        "fields": ['text'],
        "like": [
            {
                "_index": "articles",
                "_id": hit.meta.id,
            },
        ],
    }}})
    for result in mlts['hits']['hits']:
        try:
            print("    "+result['_source']['publication_date'])
            print("    Read:" + str(result['_source']['popularity']['no_read']))
        except KeyError:
            print("    Title unknown")

