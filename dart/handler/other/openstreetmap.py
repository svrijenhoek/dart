import urllib
import json
import time

from minimock import Mock


class OpenStreetMap:

    openstreetmap_url = 'https://nominatim.openstreetmap.org/search?format=json&addressdetails=2&q='

    @staticmethod
    def make_request(url):
        r"""
        >>> urllib.request = Mock('urllib.Request')
        >>> OpenStreetMap.make_request('https://nominatim.openstreetmap.org/search?format=json&addressdetails=2&q=Amsterdam')
        Called urllib.Request.urlopen(
            'https://nominatim.openstreetmap.org/search?format=json&addressdetails=2&q=Amsterdam')
        """
        page = urllib.request.urlopen(url)
        return page

    def get_coordinates(self, place):
        try:
            url = self.openstreetmap_url + place.replace(" ", "%20")
            page = self.make_request(url)
            content = json.loads(page.read())[0]
            lat = content['lat']
            lon = content['lon']
            country_code = content['address']['country_code'].upper()
            time.sleep(1)
            return lat, lon, country_code
        except KeyError:
            return 0, 0, 0
        except (urllib.error.HTTPError, urllib.error.URLError):
            return
