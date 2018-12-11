from elasticsearch import Elasticsearch

es = Elasticsearch()
mapping = {
  "mappings": {
    "_doc": {
      "properties": {
        "text": {
          "type": "text",
          "term_vector": "with_positions_offsets",
          "analyzer": "dutch"
        }
      }
    }
  }
}
es.indices.delete(index='articles')
print("Index removed")
es.indices.create(index='articles', body=mapping)
print("Index created")
