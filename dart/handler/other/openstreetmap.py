import urllib
import json


class OpenStreetMap:

    openstreetmap_url = 'https://nominatim.openstreetmap.org/search?format=json&addressdetails=2&q='

    def get_coordinates(self, place):
        try:
            page = urllib.request.urlopen(self.openstreetmap_url + place.replace(" ", "%20"))
            content = json.loads(page.read())[0]
            lat = content['lat']
            lon = content['lon']
            country_code = content['address']['country_code'].upper()
            return lat, lon, country_code
        except (IndexError, KeyError, TypeError):
            return 0, 0, 0
        except (urllib.error.HTTPError, urllib.error.URLError):
            pass
