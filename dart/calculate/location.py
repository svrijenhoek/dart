from dart.models.Article import Article
from dart.handler.elastic.recommendation_handler import RecommendationHandler
from dart.handler.elastic.article_handler import ArticleHandler
from dart.handler.elastic.connector import Connector
from dart.handler.other.openstreetmap import OpenStreetMap
import dart.Util as Util
import json, sys
import string


class AnalyzeLocations:

    def __init__(self):
        self.connector = Connector()
        self.rec_handler = RecommendationHandler()
        self.article_handler = ArticleHandler()
        self.recommendations = self.rec_handler.get_all_recommendations()
        self.openstreetmap = OpenStreetMap()
        self.printable = set(string.printable)
        try:
            self.known_locations = Util.read_json_file('../../output/known_locations.json')
        except FileNotFoundError:
            self.known_locations = {}

    def add_document(self, title, date, recommendation_type, location):
        doc = {
            'title': title,
            'date': date,
            'type': recommendation_type,
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
            # filter out special characters that would throw off a URL
            place = ''.join(filter(lambda x: x in self.printable, s))
            # filter for entities of type Location and filter out wrongly detected entities
            if entity['label'] == 'LOC' and len(place) > 2 and '|' not in place and place.lower() != 'None'.lower():
                # see if we have looked up this location before
                if place not in self.known_locations:
                    # retrieve the coordinates from OpenStreetMap
                    lat, lon, country_code = self.openstreetmap.get_coordinates(place)
                    self.known_locations[place] = [country_code, lat, lon]
                    output.append([place, [country_code, lat, lon]])
                else:
                    # do not add this location if we have no known coordinates for it
                    if not self.known_locations[place] == [0, 0, 0]:
                        output.append([place, self.known_locations[place]])
        return output

    def analyze(self, df):
        for _, recommendation in df.iterrows():
            article = Article(self.article_handler.get_by_id(recommendation.id))
            locations = self.analyze_entities(article.entities)
            for location in locations:
                self.add_document(article.title, article.publication_date, recommendation.recommendation_type, location)

    def execute(self):
        df = self.rec_handler.initialize()
        dates = df.date.unique()
        for date in dates:
            df1 = df[df.date == date]
            self.analyze(df1)
            Util.write_to_json('../../output/known_locations.json', self.known_locations)


def execute(argv):
    run = AnalyzeLocations()
    run.execute()


if __name__ == "__main__":
    execute(sys.argv[1:])
