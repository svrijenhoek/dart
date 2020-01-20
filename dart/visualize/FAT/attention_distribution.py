import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from scipy.spatial.distance import euclidean
from collections import Counter


class AttentionDistribution:

    def __init__(self, handlers, config):
        self.handlers = handlers
        self.config = config

        self.political_parties = np.array(self.config["political_parties"])

    def execute(self):
        """
        Iterate over all dates and recommendation types to calculate distance in attention distributions.
        Visualize output.
        """
        data = []
        party_data = {}
        for date in self.config["recommendation_dates"]:
            upper = datetime.strptime(date, '%d-%m-%Y')
            lower = upper - timedelta(days=self.config["recommendation_range"])
            pool = self.handlers.articles.get_all_in_timerange(lower, upper)
            for recommendation_type in self.handlers.recommendations.get_recommendation_types():
                recommendations = self.handlers.recommendations.get_recommendations_at_date(date, recommendation_type)
                if recommendations:
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
        """
        Calculate Euclidian distance between the vectors for articles in the pool of all articles and the recommended
        articles
        """
        pool_vector = self.make_vector(pool)
        recommendation_vector = self.make_vector(recommendations)
        distance = euclidean(pool_vector, recommendation_vector)
        diff = np.array(recommendation_vector) - np.array(pool_vector)
        return distance, diff

    def make_vector(self, articles):
        """
        Create a vector representing the relative representation of political parties in articles
        """
        all_vector = [0]*len(self.political_parties)
        for article in articles:
            article_vector = [0]*len(self.political_parties)
            # for each party specified in the configuration file
            for ix, party in enumerate(self.political_parties):
                # check if the party is either mentioned in one of the article's articles or mentioned in the text
                if self.in_entities(article.entities, party) or self.in_fulltext(article.text, party):
                    # binary approach; being mentioned once is enough
                    article_vector[ix] = 1
            all_vector = [x + y for x, y in zip(all_vector, article_vector)]
        # normalize for the length of the article
        if len(articles) == 0:
            return 0
        else:
            output = [x/len(articles) for x in all_vector]
            return output

    @staticmethod
    def in_entities(entities, party):
        """
        Check if the political party is mentioned in line with the article's entities.
        This means checking the political party that mentioned politicians belong to. Could be extended to also checking
        mentioned organisations, but checking the fulltext for this proved more efficient.
        """
        short_party = party[0]
        full_party = party[1]
        # only consider entities of type person
        persons = filter(lambda x: x['label'] == 'PER', entities)
        for person in persons:
            # if the person has a property 'party' (this avoids checking this value for people that are not politicians)
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

    @staticmethod
    def visualize(df):
        """
        Line plot displaying time on the x-axis and distance on the y-axis
        """
        df['date'] = pd.to_datetime(df['date'], format="%d-%m-%Y")
        df = df.sort_values('date', ascending=True)
        df.set_index('date', inplace=True)
        plt.figure()
        df.groupby('type')['distance'].plot(legend=True)
        plt.xticks(rotation='vertical')
        plt.draw()
        print(df.groupby('type')['distance'].mean())

    def visualize_party(self, data):
        """
        Bar plot visualizing for each party how often they are mentioned significantly more or less than was to be
        expected from the pool
        """
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
        bars2 = [data['custom'][label] for label in labels]
        # bars3 = [data['more_like_this'][label] for label in labels]
        # bars4 = [data['political'][label] for label in labels]

        # Set position of bar on X axis
        r1 = np.arange(len(bars1))
        r2 = [x + barWidth for x in r1]
        # r3 = [x + barWidth for x in r2]
        # r4 = [x + barWidth for x in r3]

        # Make the plot
        plt.bar(r1, bars1, width=barWidth, edgecolor='white', label='random')
        plt.bar(r2, bars2, width=barWidth, edgecolor='white', label='custom')
        # plt.bar(r3, bars3, width=barWidth, edgecolor='white', label='more_like_this')
        # plt.bar(r4, bars4, width=barWidth, edgecolor='white', label='political')

        # Add xticks on the middle of the group bars
        plt.xlabel('parties', fontweight='bold')
        plt.xticks([r + barWidth for r in range(len(bars1))], labels, rotation='vertical')

        # Create legend & Show graphic
        plt.legend()
        plt.show()



