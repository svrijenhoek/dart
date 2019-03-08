from dart.handler.elastic.connector import Connector
import math


# basically copied from https://www.datasciencecentral.com/profiles/blogs/
# document-similarity-analysis-using-elasticsearch-and-python
class CosineSimilarity:

    connector = Connector()

    @staticmethod
    def create_dictionary(doc):
        return dict([(k, v['term_freq'])
                     for k, v in doc
                    .get('term_vectors')
                    .get('text')
                    .get('terms')
                    .items()])

    @staticmethod
    def cosine(vec1, vec2):
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum([vec1[x] * vec2[x] for x in intersection])
        sum1 = sum([vec1[x]**2 for x in vec1.keys()])
        sum2 = sum([vec2[x]**2 for x in vec2.keys()])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)
        if not denominator:
            return 0.0
        else:
            return float(numerator) / denominator

    def calculate_cosine_similarity(self, doc_list):
        tv_list = [self.connector.get_term_vector('articles', '_doc', doc) for doc in doc_list]
        dict_list = [self.create_dictionary(tv) for tv in tv_list]
        output = []
        for x in range(0, len(dict_list)):
            for y in range(0, len(dict_list)):
                if y > x:
                    output.append(self.cosine(dict_list[x], dict_list[y]))
        return output
