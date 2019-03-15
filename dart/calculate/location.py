from dart.models.Article import Article
from dart.models.Recommendation import Recommendation
from dart.handler.elastic.recommendation_handler import RecommendationHandler
from dart.handler.elastic.article_handler import ArticleHandler
from dart.handler.elastic.connector import Connector
import dart.Util as Util
import pandas as pd
import json
import urllib
import string


class AnalyzeLocations:

    openstreetmap_url = 'https://nominatim.openstreetmap.org/search?format=json&addressdetails=2&q='
    printable = set(string.printable)

    def __init__(self):
        self.connector = Connector()
        self.rec_handler = RecommendationHandler()
        self.article_handler = ArticleHandler()
        self.recommendations = self.rec_handler.get_all_documents()
        try:
            self.known_locations = Util.read_json_file('../../output/known_locations.json')
        except FileNotFoundError:
            self.known_locations = {}

    def initialize(self):
        table = [Recommendation(x).source for x in self.recommendations]
        df = pd.DataFrame.from_dict(table)
        return df

    def add_document(self, title, date, type, location):
        doc = {
            'title': title,
            'date': date,
            'type': type,
            'text': location[0],
            'country_code': location[1][0],
            'location': {
                'lat': location[1][1],
                'lon': location[1][2]
            }
        }
        body = json.dumps(doc)
        self.connector.add_document('locations', '_doc', body)

    def analyze_entities(self, entities):
        output = []
        for entity in entities:
            s = entity['text']
            place = ''.join(filter(lambda x: x in self.printable, s))
            if entity['label'] == 'LOC' and len(place) > 2 and '|' not in place and place.lower() != 'None'.lower():
                if place not in self.known_locations:
                    try:
                        page = urllib.request.urlopen(self.openstreetmap_url + place.replace(" ", "%20"))
                        content = json.loads(page.read())[0]
                        lat = content['lat']
                        lon = content['lon']
                        country_code = content['address']['country_code'].upper()
                        self.known_locations[place] = [country_code, lat, lon]
                        output.append([place, [country_code, lat, lon]])
                    except (IndexError, KeyError):
                        self.known_locations[place] = [0, 0, 0]
                    except (urllib.error.HTTPError, urllib.error.URLError):
                        pass
                else:
                    if not self.known_locations[place] == [0, 0, 0]:
                        output.append([place, self.known_locations[place]])
        return output

    def analyze(self, df):
        for index, row in df.iterrows():
            for recommendation in row.recommendations:
                article_list = row.recommendations[recommendation]
                for article_id in article_list:
                    article = Article(self.article_handler.get_by_id(article_id))
                    locations = self.analyze_entities(article.entities)
                    for location in locations:
                        self.add_document(article.title, article.publication_date, recommendation, location)
        print(self.known_locations)

    def execute(self):
        df = self.initialize()
        dates = df.date.unique()
        for date in dates:
            df1 = df[df.date == date]
            self.analyze(df1)
            Util.write_to_json('../../output/known_locations.json', self.known_locations)


def execute():
    run = AnalyzeLocations()
    run.execute()

