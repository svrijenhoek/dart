import sys
from dart.handler.elastic.connector import Connector
from dart.handler.elastic.article_handler import ArticleHandler
from dart.models.Article import Article

searcher = ArticleHandler()
connector = Connector()


def execute():
    body = {
        "size": 1000,
        "query": {
            "match_all": {}
        }
    }
    sid, scroll_size = searcher.execute_search_with_scroll('articles', body)
    # Start scrolling
    while scroll_size > 0:
        print("Scrolling...")
        result = searcher.scroll(sid, '2m')
        # Update the scroll ID
        sid = result['_scroll_id']
        # Get the number of results that we returned in the last scroll
        scroll_size = len(result['hits']['hits'])
        print("scroll size: " + str(scroll_size))
        # Do something with the obtained page
        for hit in result['hits']['hits']:
            document = Article(hit)
            body = {
                "doc": {'htmlsource': ''}
            }
            connector.update_document('articles', '_doc', document.id, body)


def main(argv):
    execute()


if __name__ == "__main__":
    main(sys.argv[1:])
