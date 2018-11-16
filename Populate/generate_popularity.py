from Elastic.Connector import Connector
from Elastic.Search import Search
import urllib.request
import json
import time


connector = Connector()
search = Search()
offset = 0
size = 10000

facebook_graph_url = 'https://graph.facebook.com/?id='


def get_graph_info(url):
    page = urllib.request.urlopen(facebook_graph_url + url)
    content = json.loads(page.read())
    comments = content['share']['comment_count']
    shares = content['share']['share_count']
    return comments, shares


non_successful_list = []

results = search.get_all_documents('articles', size, offset)
total = len(results)
while offset < total:
    results = search.get_all_documents('articles', size, offset)
    for hit in results:
        try:
            docid = hit['_id']
            url = hit['_source']['url']
            if 'facebook_share' not in hit['_source']['popularity']:
                comment_count, share_count = get_graph_info(url)
                print(hit['_source']['title'])
                print("Share count: %d, Comment count: %d" % (share_count, comment_count))
                body = {"doc": {"popularity": {"facebook_share": int(share_count), "facebook_comment": int(comment_count)}}}
                connector.update_document('articles', 'text', docid, body)
                time.sleep(2)
            else:
                print(url + " already has popularity metrics")
        except KeyError:
            print("URL not found")
        except urllib.error.HTTPError:
            print("Graph API limit reached")
            non_successful_list.append(hit)
            time.sleep(1800)
    offset += size

while non_successful_list:
    for x in non_successful_list[:]:
        try:
            docid = x['_id']
            url = x['_source']['url']
            comment_count, share_count = get_graph_info(url)
            print(x['_source']['title'])
            print("Share count: %d, Comment count: %d" % (share_count, comment_count))
            body = {"doc": {"popularity": {"facebook_share": int(share_count), "facebook_comment": int(comment_count)}}}
            connector.update_document('articles', 'text', docid, body)
            non_successful_list.remove(x)
            time.sleep(2)
        except urllib.error.HTTPError:
            print("Graph API limit reached")
            time.sleep(1800)





