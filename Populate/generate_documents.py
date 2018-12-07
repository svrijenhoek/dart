import json
import os

from Elastic.Connector import Connector
from Elastic.Search import Search
from NLP.Annotator import Annotator

import Util


connector = Connector()
searcher = Search()
annotator = Annotator()

root = Util.read_config_file("general", "data_folder")

count_total = 0
count_fault = 0
count_success = 0


def add_document(doc):
    # see if the user has specified their own id. If this is the case, use this in Elasticsearch,
    # otherwise generate a new one based on the title and publication date
    if 'id' not in doc:
        try:
            doc_id = Util.generate_hash(doc['title'] + doc['publication_date'])
            doc['id'] = doc_id
        except KeyError:
            return -1
    # add NLP annotation if this wasn't done already
    if 'entities' or 'dependencies' not in doc:
        try:
            annotated_doc, entities, dependencies = annotator.annotate(doc["text"])
            doc['entities'] = entities
            doc['dependencies'] = dependencies
        except KeyError:
            return -1
    # add popularity metrics
    if 'popularity' not in doc:
        doc['popularity'] = {'calculated': 'no'}
    body = json.dumps(doc)
    connector.add_document('articles', doc['id'], '_doc', body)
    return 1


# iterate over all the files in the data folder
for path, subdirs, files in os.walk(root):
    for name in files:
        print(count_total)
        # assumes all files are json-l, change this to something more robust!
        for line in open((os.path.join(path, name))):
            count_total += 1
            json_doc = json.loads(line)
            success = add_document(json_doc)
            count_total += 1
            if success == 1:
                count_success += 1
            else:
                count_fault += 1


print("Total number of documents: "+str(count_total))
print("Errors: "+str(count_fault))
print("Success: "+str(count_success))
