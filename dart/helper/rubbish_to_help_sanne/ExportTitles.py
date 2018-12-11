import Util
import sys
from Elastic.Search import Search

results = []
searcher = Search()

def execute():
    size = 500
    offset = 0
    docs = searcher.get_all_documents_with_offset('articles', size, offset)
    while len(docs) > 0:
        print(offset)
        for doc in docs:
            try:
                id = doc['_id']
                title = doc['_source']['title'],
                source = doc['_source']['doctype']
                results.append({
                    "id": id,
                    "title": title,
                    "source": source
                })
            except KeyError:
                continue
        offset += size
        docs = searcher.get_all_documents_with_offset('articles', size, offset)

    Util.write_to_json('nodes.json', results)
    print(results)


def main(argv):
    execute()


if __name__ == "__main__":
    main(sys.argv[1:])
