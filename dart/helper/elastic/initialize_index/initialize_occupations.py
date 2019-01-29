from elasticsearch import Elasticsearch

es = Elasticsearch()
mapping = {
  "mappings": {
    "_doc": {
      "properties": {
        "date": {
          "type": "date",
          "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis||dd-MM-YYYY"
        },
      }
    }
  }
}
es.indices.delete(index='occupations')
print("Index removed")
es.indices.create(index='occupations', body=mapping)
print("Index created")
