import pandas as pd
from datetime import datetime, timedelta
from scipy.spatial.distance import euclidean
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter


class AttentionDistribution:

    def __init__(self, handlers, config):
        self.handlers = handlers
        self.config = config

        self.political_parties = np.array(self.config["political_parties"])

    def execute(self):
        data = []
        party_data = {}
        for date in self.config["recommendation_dates"]:
            print(date)
            upper = datetime.strptime(date, '%d-%m-%Y')
            lower = upper - timedelta(days=self.config["recommendation_range"])
            pool = self.handlers.articles.get_all_in_timerange(lower, upper)
            for recommendation_type in self.handlers.recommendations.get_recommendation_types():
                recommendations = self.handlers.recommendations.get_recommendations_at_date(date, recommendation_type)
                distances = []
                if recommendation_type not in party_data:
                    party_data[recommendation_type] = Counter()
                for recommendation in recommendations:
                    articles = self.handlers.articles.get_multiple_by_id(recommendation.articles)
                    distance, diff = self.calculate(pool, articles)
                    distances.append(distance)
                    too_big = self.political_parties[:, 0][diff > 0.2]
                    for party in too_big:
                        party_data[recommendation_type][party] += 1
                data.append({'date': date, 'type': recommendation_type, 'distance': np.mean(distances)})
        df = pd.DataFrame(data)
        self.visualize(df)
        self.visualize_party(party_data)

    def calculate(self, pool, recommendations):
        pool_vector = self.make_vector(pool)
        recommendation_vector = self.make_vector(recommendations)
        distance = euclidean(pool_vector, recommendation_vector)
        diff = np.array(recommendation_vector) - np.array(pool_vector)
        return distance, diff

    def make_vector(self, articles):
        all_vector = [0]*len(self.political_parties)
        for article in articles:
            article_vector = [0]*len(self.political_parties)
            for ix, party in enumerate(self.political_parties):
                if self.in_entities(article.entities, party) or self.in_fulltext(article.text, party):
                    article_vector[ix] = 1
            all_vector = [x + y for x, y in zip(all_vector, article_vector)]
        output = [x/len(articles) for x in all_vector]
        return output

    @staticmethod
    def in_entities(entities, party):
        short_party = party[0]
        full_party = party[1]
        persons = filter(lambda x: x['label'] == 'PER', entities)
        for person in persons:
            if 'parties' in person:
                if short_party in person['parties'] or full_party in person['parties']:
                    return True
        return False

    @staticmethod
    def in_fulltext(text, party):
        short_party = party[0]
        full_party = party[1]
        if short_party in text or full_party in text:
            return True
        else:
            return False

    def visualize(self, df):
        df['date'] = pd.to_datetime(df['date'], format="%d-%m-%Y")
        df = df.sort_values('date', ascending=True)
        df.set_index('date', inplace=True)
        plt.figure()
        df.groupby('type')['distance'].plot(legend=True)
        plt.draw()
        print(df.groupby('type')['distance'].mean())

    def visualize_party(self, data):
        plt.figure()
        labels = self.political_parties[:, 0]
        # set width of bar
        barWidth = 0.20

        for recommendation_type in data:
            for label in labels:
                if label not in data[recommendation_type]:
                    data[recommendation_type][label] = 0

        # set height of bar
        bars1 = [data['random'][label] for label in labels]
        bars2 = [data['most_popular'][label] for label in labels]
        bars3 = [data['more_like_this'][label] for label in labels]
        bars4 = [data['political'][label] for label in labels]

        # Set position of bar on X axis
        r1 = np.arange(len(bars1))
        r2 = [x + barWidth for x in r1]
        r3 = [x + barWidth for x in r2]
        r4 = [x + barWidth for x in r3]

        # Make the plot
        plt.bar(r1, bars1, width=barWidth, edgecolor='white', label='random')
        plt.bar(r2, bars2, width=barWidth, edgecolor='white', label='most_popular')
        plt.bar(r3, bars3, width=barWidth, edgecolor='white', label='more_like_this')
        plt.bar(r4, bars4, width=barWidth, edgecolor='white', label='political')

        # Add xticks on the middle of the group bars
        plt.xlabel('parties', fontweight='bold')
        plt.xticks([r + barWidth for r in range(len(bars1))], labels)

        # Create legend & Show graphic
        plt.legend()
        plt.show()



