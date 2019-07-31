import os
import json
import csv

root = "data\\articles\\"
root_with_popularity = "data\\with_popularity\\"
popularity_file = "C:\\Users\\Sanne\\Downloads\\popularity.csv"


def read_from_file():
    mapping = {}
    with open(popularity_file, mode='r') as csv_file:
        next(csv_file)
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            title = row[3]
            popularity = row[2].replace(',', '')
            mapping[title] = popularity
    return mapping


mapping = read_from_file()
print(mapping)
for path, _, files in os.walk(root):
    for name in files:
        print(os.path.join(path, name))
        # assumes all files are json-l, change this to something more robust!
        for line in open((os.path.join(path, name))):
            json_doc = json.loads(line)
            try:
                try:
                    del json_doc['htmlsource']
                except KeyError:
                    pass
                title = json_doc['title']
                json_doc['popularity'] = mapping[title]
                with open(os.path.join(root_with_popularity, name), 'a') as outfile:
                    json.dump(json_doc, outfile)
                    outfile.write("\n")
            except KeyError:
                with open(os.path.join(root_with_popularity, name), 'a') as outfile:
                    json.dump(json_doc, outfile)
                    outfile.write("\n")
            except json.JSONDecodeError:
                continue
