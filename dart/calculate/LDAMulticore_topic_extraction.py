from dart.helper.elastic.querybuilder import QueryBuilder
from dart.helper.elastic.connector import Connector
from dart.models.Article import Article
import dart.Util
from nltk.stem.snowball import DutchStemmer
from gensim import corpora, models
import spacy
from operator import itemgetter
from collections import OrderedDict

searcher = QueryBuilder()
connector = Connector()
ner = spacy.load('nl_core_news_sm', disable=['parser', 'tagger'])
pos = spacy.load('nl_core_news_sm', disable=['ner', 'parser'])
model_location = '../../output/ldamodel_august'
document_location = '../../output/august_documents.pkl'
test_location = '../../output/august_test_documents.pkl'

stemmer = DutchStemmer()


def get_documents(l, u):
    docs = []
    docs_in_range = searcher.get_all_in_timerange('articles', l, u)
    for doc in docs_in_range:
        article = Article(doc)
        docs.append([article.title, article.text])
    return docs


def clean(doc):
    ner_doc = ner(doc)
    text = " ".join(token.text for token in ner_doc)
    # for ent in ner_doc.ents:
    #     if ent.label_ == 'PER':
    #         text = text.replace(ent.text, "PERSON")
    #     elif ent.label_ == 'ORG':
    #         text = text.replace(ent.text, "ORGANIZATION")
    pos_doc = pos(text)
    tokens = " ".join([i.text for i in pos_doc if i.pos_ == 'NOUN'])
    stemmed = " ".join(stemmer.stem(word) for word in tokens.split())
    return stemmed


def clean_data(data, save_location):
    print("Cleaning documents")
    cleaned = [clean(x[1]) for x in data]
    dart.Util.save_data(save_location, cleaned)
    return cleaned


def prepare(data):
    c = [x.split() for x in data]
    d = corpora.Dictionary(c)
    m = [d.doc2bow(doc) for doc in c]
    return c, d, m


def train_lda_model(m, d):
    print("Train model")
    model = models.LdaMulticore(m, id2word=d, num_topics=50, passes=300)
    model.save(model_location)
    print(model.print_topics(num_topics=50, num_words=5))
    return model


def load_model():
    return models.LdaMulticore.load(model_location)


def evaluate(m):
    print("Evaluating testset")
    result = {9999: []}
    for idx, val in enumerate(m):
        if val:
            vector = lda[val]
            max_category = max(vector, key=itemgetter(1))
            confidence = max_category[1]
            category = max_category[0]
            title = testset[idx][0]
            if confidence > 0.8:
                if category in result:
                    array = result[category]
                    array.append(title)
                    result[category] = array
                else:
                    result[category] = [title]
            else:
                result[9999].append(title)
    return result


def print_result():
    b = OrderedDict(sorted(output.items()))
    for key in b:
        matches = output[key]
        print(key)
        if key != 9999:
            terms = lda.print_topic(key, 10)
            print(terms)
        for match in matches:
            print("\t{}".format(match))


if __name__ == '__main__':
    clean_all = True
    clean_test_data = True
    train_model = True
    if train_model:
        print('Initializing')
        documents = get_documents('01-01-2017', '01-02-2017')
        if clean_all:
            cleaned_documents = clean_data(documents, document_location)
        else:
            cleaned_documents = dart.Util.load_data(document_location)
        corpus, dictionary, matrix = prepare(cleaned_documents)
        lda = train_lda_model(matrix, dictionary)
    else:
        lda = load_model()

    print("Retrieving testset")
    testset = get_documents('01-01-2017', '01-02-2017')

    if clean_test_data:
        test = clean_data(testset, test_location)
    else:
        test = dart.Util.load_data(test_location)

    t_corpus, t_dict, t_matrix = prepare(test)
    output = evaluate(t_matrix)
    print_result()


