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

# iterate over all the files in the data folder
for path, subdirs, files in os.walk(root):
    for name in files:
        # assumes all files are json-l, change this to something more robust!
        for line in open((os.path.join(path, name))):
            count_total += 1
            json_doc = json.loads(line)
            # see if the user has specified their own id. If this is the case, use this in Elasticsearch,
            # otherwise generate a new one based on the title and publication date
            if 'id' not in json_doc:
                try:
                    doc_id = Util.generate_hash(json_doc['title']+json_doc['publication_date'])
                    json_doc['id'] = doc_id
                except KeyError:
                    print('Title or publication date not found')
                    count_fault += 1
                    continue
            # add NLP annotation if this wasn't done already
            if 'entities' or 'dependencies' not in json_doc:
                try:
                    doc, entities, dependencies = annotator.annotate(json_doc["text"])
                    json_doc['entities'] = entities
                    json_doc['dependencies'] = dependencies
                except KeyError:
                    print("Text could not be loaded")
                    count_fault += 1
                    continue
            # add popularity metrics
            if 'popularity' not in json_doc:
                doctype = json_doc['doctype']
                try:
                    json_doc['popularity'] = {'calculated': 'no'}
                except KeyError:
                    print("url could not be found in the configuration")
                    count_fault += 1
                    continue

            body = json.dumps(json_doc)
            connector.add_document('articles', json_doc['id'], 'text', body)
            count_success += 1
            print(count_total)

print("Total number of documents: "+str(count_total))
print("Errors: "+str(count_fault))
print("Success: "+str(count_success))
