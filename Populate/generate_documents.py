import json
import os
import hashlib
import numpy as np

from Elastic.Connector import Connector
from NLP.Annotator import Annotator

import Util


connector = Connector()
annotator = Annotator()

root = "..\\data\\articles\\"
count_total = 0
count_fault = 0
count_success = 0
keys = ["text", "start_char", "end_char", "type"]

# index articles
for path, subdirs, files in os.walk(root):
    for name in files:
        for line in open((os.path.join(path, name))):
            count_total += 1
            json_doc = json.loads(line)
            # check id
            if 'id' not in json_doc:
                try:
                    hash_id = hashlib.sha1((json_doc['title']+json_doc['publication_date']).encode('utf-8')).hexdigest()
                    json_doc['id'] = hash_id
                except KeyError:
                    print('Title or publication date not found')
                    count_fault += 1
                    continue
            # add NLP annotation
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
                    config_values = Util.read_config_file('popularity', doctype)
                    no_read = int(np.random.normal(config_values['mean'], config_values['sdev']))
                    json_doc['popularity'] = {'no_read': no_read}
                except KeyError:
                    print("doctype could not be found in the configuration")
                    count_fault += 1
                    continue

            body = json.dumps(json_doc)
            connector.add_document('articles', json_doc['id'], 'text', body)
            count_success += 1
            print(count_total)

print("Total number of documents: "+str(count_total))
print("Errors: "+str(count_fault))
print("Success: "+str(count_success))
