from Elastic.Connector import Connector
from Elastic.Search import Search

import sys, math


class CosineSimilarity:

    connector = Connector()

    def create_dictionary(self, doc):
        return dict([(k, v['term_freq'])
                     for k, v in doc
                    .get('term_vectors')
                    .get('text')
                    .get('terms')
                    .items()])

    def cosine(self, vec1, vec2):
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum([vec1[x] * vec2[x] for x in intersection])
        sum1 = sum([vec1[x]**2 for x in vec1.keys()])
        sum2 = sum([vec2[x]**2 for x in vec2.keys()])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)
        if not denominator:
            return 0.0
        else:
            return float(numerator) / denominator

    def calculate_cosine_similarity(self, doc1, doc2):
        tv1 = self.connector.get_term_vector('termvectors', '_doc', doc1)
        tv2 = self.connector.get_term_vector('termvectors', '_doc', doc2)
        dict1 = self.create_dictionary(tv1)
        dict2 = self.create_dictionary(tv2)
        return self.cosine(dict1, dict2)


# def main(argv):
#     searcher = Search()
#     cs = CosineSimilarity()
#     doc1 = searcher.get_random_document('articles')[0]
#     print(doc1['_source']['title'])
#     doc2 = searcher.get_random_document('articles')[0]
#     print(doc2['_source']['title'])
#     cs.calculate_cosine_similarity(doc1, doc2)
#
# if __name__ == "__main__":
#     main(sys.argv[1:])
