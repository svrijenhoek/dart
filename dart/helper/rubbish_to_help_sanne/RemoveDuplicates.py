from Elastic.Search import Search
from Elastic.Connector import Connector
from textpipe import doc, pipeline


searcher = Search()
connector = Connector()
size = 1000
offset = 0

fault = 0

file = {}

# documents = searcher.get_popularity_calculated_with_offset(offset)
# while len(documents) > 0:
#     for doc in documents:
#         try:
#             url = doc['_source']['url']
#             shares = doc['_source']['popularity']['facebook_share']
#             file[url] = shares
#         except KeyError:
#             fault += 1
#     offset += size
#     documents = searcher.get_popularity_calculated_with_offset(offset)

# with open('data.json', 'w') as outfile:
#     json.dump(file, outfile)
#
# success = 0
# fault = 0
# with open('data.json') as data_file:
#     data = json.load(data_file)
#     for url in data:
#         try:
#             print(url)
#             doc = searcher.get_by_url('articles', url)
#             pq.add_popularity(doc['_id'], data[url], 0)
#             success += 1
#         except IndexError:
#             fault += 1
# print(success)
# print(fault)

print("Initializing")
pipe = pipeline.Pipeline(['NWords', 'Complexity', 'NSentences'], 'nl')
documents = searcher.get_not_calculated('stylometrics.complexity')
while len(documents) > 0:
    for document in documents:
        try:
            docid = document['_id']
            source = searcher.get_by_id('articles', docid)['_source']
            text = source['text']
            try:
                tp_doc = pipe(text)
                complexity = tp_doc['Complexity']
                nwords = tp_doc['NWords']
                nsentences = tp_doc['NSentences']
                body = {
                    "doc": {
                        "stylometrics": {
                            "complexity": float(complexity),
                            "nwords": float(nwords),
                            "nsentences": float(nsentences)}}}
                connector.update_document('articles', '_doc', docid, body)
            except ValueError:
                continue
        except KeyError:
            fault += 1
    offset += size
    documents = searcher.get_not_calculated('stylometrics.complexity')
    print(offset)

