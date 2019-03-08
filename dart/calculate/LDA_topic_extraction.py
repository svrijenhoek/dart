from dart.handler.elastic.article_handler import ArticleHandler
from dart.handler.elastic.connector import Connector
from dart.models.Article import Article
from nltk.corpus import stopwords
from nltk.stem.snowball import DutchStemmer
import string
import gensim
from datetime import datetime, timedelta
from gensim import corpora
import spacy

searcher = ArticleHandler()
connector = Connector()
nlp = spacy.load('nl_core_news_sm')

stop = set(stopwords.words('dutch'))
exclude = set(string.punctuation)
stemmer = DutchStemmer()


def get_articles_on_date(date):
    lower = datetime.strptime(date, '%d-%m-%Y')
    upper = datetime.strptime(date, '%d-%m-%Y') + timedelta(days=365)
    response = searcher.get_all_in_timerange('articles', 9000, lower, upper)
    articles = [{'id': x['_id'], 'text': x['_source']['text'], 'title': x['_source']['title']} for x in response]
    return articles


def clean(doc):
    analyzed = nlp(doc)
    nouns = " ".join([i.text for i in analyzed if i.pos_ == 'NOUN'])
    normalized = " ".join(stemmer.stem(word) for word in nouns.split())
    return normalized


print('Initializing')
doc_clean = []
body = {
    "query": {
        "match_all": {}
    }
}
sid, scroll_size = searcher.execute_search_with_scroll('articles', body)
# Start scrolling
while scroll_size > 0:
    print("Scrolling...")
    result = searcher.scroll(sid, '2m')
    # Update the scroll ID
    sid = result['_scroll_id']
    # Get the number of results that we returned in the last scroll
    scroll_size = len(result['hits']['hits'])
    print("scroll size: " + str(scroll_size))
    # Do something with the obtained page
    for hit in result['hits']['hits']:
        document = Article(hit)
        doc_clean.append(document.text.split())

doc_clean = [clean(doc['text']).split() for doc in articles]
dictionary = corpora.Dictionary(doc_clean)
doc_term_matrix = [dictionary.doc2bow(doc) for doc in doc_clean]

Lda = gensim.models.ldamodel.LdaModel
ldamodel = Lda(doc_term_matrix, num_topics=100, id2word=dictionary, passes=100)
print(ldamodel.print_topics(num_topics=100, num_words=5))

# output = {}
# for idx, val in enumerate(doc_term_matrix):
#     vector = ldamodel[val]
#     category = vector[0][0]
#     title = articles[idx]['title']
#     if category in output:
#         array = output[category]
#         array.append(title)
#         output[category] = array
#     else:
#         output[category] = [title]
# print(output)

