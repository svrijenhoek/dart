import dart.Util
from dart.handler.elastic.article_handler import ArticleHandler
from dart.handler.elastic.recommendation_handler import RecommendationHandler
from dart.models.Article import Article
from dart.models.Recommendation import Recommendation
import numpy as np
from whoswho import who


class FindDutchPoliticians:

    def __init__(self):
        # initialize the list of known politicians from file
        file = dart.Util.read_json_file('../../output/politicians.json')
        self.politicians = [x['name'] for x in file]
        self.article_handler = ArticleHandler()
        self.recommendation_handler = RecommendationHandler()

    @staticmethod
    def same_name(longer, shorter):
        """
        Method that determines whether two names are the same, think of 'John Smith'vs. 'J. Smith' vs 'Smith'.
        Requires extensively more work!
        All names that include a '.' have likely been detected wrongly, therefore return False.
        Otherwise we check if the longer name ends with the shorter one (relevant for the situation when only a
        last name is mentioned. Lastly, ask the 'whois' package (does not work terribly well).
        >>> FindDutchPoliticians.same_name("Barack Obama", "Obama")
        True
        >>> FindDutchPoliticians.same_name("Donald", "Donald Trump")
        False
        >>> FindDutchPoliticians.same_name("Sybrand Buma", "Sybrand Reinier Buma")
        True
        """
        if '.' in longer:
            return False
        if longer.lower().endswith(shorter.lower()):
            return True
        return who.match(longer, shorter)

    def find_politicians(self, mentions):
        """
        Method that compares found mentions with a list of known politicians (from Wikidata).
        """
        politicians = {}
        # for each mention detected in the test
        for mention in mentions:
            # compare to the list of previously found politicians
            for politician in self.politicians:
                if self.same_name(mention, politician):
                    politicians[mention] = mentions[mention]
        return politicians

    def mentioned_at(self, person, mentions):
        for mention in mentions:
            if len(mention) > len(person):
                longer = mention
                shorter = person
            else:
                longer = person
                shorter = mention
            if self.same_name(longer, shorter):
                return longer, mention
        return -1, -1

    def compress_person_list(self, persons):
        mentions = {}
        for person in persons:
            person = person.replace('|', '').strip()
            index, original = self.mentioned_at(person, mentions)
            if index == -1:
                mentions[person] = 1
            else:
                try:
                    mentions[index] = mentions[index] + 1
                except KeyError:
                    mentions[index] = mentions[original] + 1
                    del mentions[original]
        return mentions

    def find_mentioned_persons(self, entities):
        persons = []
        for entity in entities:
            if entity['label'] == 'PER':
                persons.append(entity['text'])
        mentions = self.compress_person_list(persons)
        return mentions

    def execute(self):
        # maintain a list of documents that have been checked before during this run to save computation time
        checked_documents = {}
        recommendations = [Recommendation(i) for i in self.recommendation_handler.get_all_documents()]
        for recommendation in recommendations:
            docid = recommendation.article.id
            if docid not in checked_documents:
                document = Article(self.article_handler.get_by_id(docid))
                mentions = self.find_mentioned_persons(document.entities)
                politicians = self.find_politicians(mentions)
                if len(politicians) > 0:
                    sum_mentions = np.sum([value for key, value in mentions.items()])
                    sum_politicians = np.sum([value for key, value in politicians.items()])
                    print(document.title)
                    print(mentions)
                    print(politicians)
                    ratio = sum_politicians / sum_mentions
                    checked_documents[recommendation.id] = ratio
                    print(ratio)
                else:
                    checked_documents[recommendation.id] = -1
            else:
                print("Document already found")
                print("{}: {}".format(recommendation.id, checked_documents[recommendation.id]))

