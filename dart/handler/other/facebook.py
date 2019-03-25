import urllib
import json
import logging
import time


class RetrieveFacebook:

    facebook_graph_url = 'https://graph.facebook.com/?id='
    module_logging = logging.getLogger('popularity')

    def make_request(self, url):
        try:
            page = urllib.request.urlopen(self.facebook_graph_url + url)
            content = json.loads(page.read())
        except urllib.error.HTTPError:
            self.module_logging.error("Graph API max reached")
            time.sleep(1800)
        return content

    def get_facebook_info(self, url):
        content = self.make_request(url)
        comments = content['share']['comment_count']
        shares = content['share']['share_count']
        return comments, shares
