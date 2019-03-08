import dart.Util
from dart.handler.elastic.article_handler import ArticleHandler
from dart.models.Article import Article
from dart.models.Recommendation import Recommendation
import sys
import numpy as np
from whoswho import who


class FindDutchPoliticians:

    def __init__(self):
        file = dart.Util.read_json_file('../../output/politicians.json')
        self.politicians = [x['name'] for x in file]
        self.article_handler = ArticleHandler()

    # Method that determines whether two names are the same, think of 'John Smith'vs. 'J. Smith' vs 'Smith'.
    # Requires extensively more work!
    # All names that include a '.' have likely been detected wrongly, therefore return False.
    # Otherwise we check if the longer name ends with the shorter one (relevant for the situation when only a
    # last name is mentioned. Lastly, ask the 'whois' package (does not work terribly well).
    @staticmethod
    def same_name(longer, shorter):
        if '.' in longer:
            return False
        if longer.lower().endswith(shorter.lower()):
            return True
        return who.match(longer, shorter)

    # Method that compares found mentions with a list of known politicians (from Wikidata).
    def find_politicians(self, mentions):
        politicians = {}
        for mention in mentions:
            for politician in self.politicians:
                if self.same_name(mention, politician):
                    politicians[mention] = mentions[mention]
        return politicians

    def mentioned_at(self, person, mentions):
        for index, mention in enumerate(mentions):
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
        checked_documents = {}
        recommendations = [Recommendation(i) for i in self.article_handler.get_all_documents('recommendations')]
        for recommendation in recommendations:
            for type in recommendation.get_recommendation_types():
                for docid in recommendation.recommendations[type]:
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
                            checked_documents[docid] = ratio
                            print(ratio)
                        else:
                            checked_documents[docid] = -1
                    else:
                        print("Document already found")
                        print("{}: {}".format(docid, checked_documents[docid]))



def main(argv):
    run = FindDutchPoliticians()
    run.execute()


if __name__ == "__main__":
    main(sys.argv[1:])
