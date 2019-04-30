import urllib
import json
import logging
import time
import requests


class RetrieveFacebook:

    facebook_graph_url = 'https://graph.facebook.com/?fields=engagement{share_count}&id='
    module_logging = logging.getLogger('popularity')

    def get_access_token(self):
        url = 'https://graph.facebook.com/oauth/access_token'
        payload = {
            'grant_type': 'client_credentials',
            'client_id': '******',
            'client_secret': '*****'
        }
        response = requests.post(url, params=payload)
        return response.json()['access_token']

    def make_request(self, url):
        try:
            full_url = self.facebook_graph_url + url+'&access_token='+self.get_access_token()
            page = urllib.request.urlopen(full_url)
            content = json.loads(page.read())
        except urllib.error.HTTPError:
            self.module_logging.error("Graph API max reached")
            time.sleep(1800)
            content = self.make_request(url)
        return content

    def get_facebook_info(self, url):
        content = self.make_request(url)
        shares = content['engagement']['share_count']
        return shares
