from dart.handler.elastic.article_handler import ArticleHandler
from dart.models.Article import Article
import dart.Util
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import re
import nltk
import pandas as pd
from nltk.stem.snowball import SnowballStemmer

stopwords = nltk.corpus.stopwords.words('dutch')
stopwords.extend(['maandag', 'dinsdag', 'woensdag', 'donderdag', 'vrijdag', 'zaterdag', 'zondag', 'weekend', 'week'])
stemmer = SnowballStemmer("dutch")
searcher = ArticleHandler()
test_location = '../../output/august_test_documents.pkl'


def get_documents(l, u):
    all_titles = []
    all_texts = []
    hits = searcher.get_all_in_timerange('articles', l, u)
    for hit in hits:
        document = Article(hit)
        # clean each document and add to result set
        all_titles.append(document.title)
        all_texts.append(document.text)
    return all_titles, all_texts


def tokenize_only(text):
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word.lower() for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z]', token):
            filtered_tokens.append(token)
    return filtered_tokens


def create_vocabulary(t):
    vocab = []
    for i in t:
        tokenized = tokenize_only(i)
        vocab.extend(tokenized)
    return vocab


if __name__ == '__main__':
    print("Retrieve documents")
    documents = dart.Util.load_data(test_location)
    titles, texts = get_documents('01-01-2017', '01-02-2017')
    vocabulary = create_vocabulary(documents)
    # print("Start analyzing")
    # texts = [doc[1] for doc in documents]

    tfidf_vectorizer = TfidfVectorizer(max_df=0.5, max_features=1000,
                                       min_df=10, stop_words=stopwords,
                                       use_idf=True, ngram_range=(1, 3))

    print("Fit vector")
    tfidf_matrix = tfidf_vectorizer.fit_transform(documents)  # fit the vectorizer to texts
    print(tfidf_vectorizer.get_feature_names())
    print("Calculate distances")
    dist = 1 - cosine_similarity(tfidf_matrix)

    length = len(dist)
    for x in range(length):
        for y in range(len(dist[x])):
            entry = dist[x,y]
            if entry < 0.3 and entry > 0.001:
                print(entry)
                print(titles[x])
                print(texts[x])
                print(documents[x])
                print(titles[y])
                print(texts[y])
                print(documents[y])
                print()

    num_clusters = 30

    km = KMeans(n_clusters=num_clusters)
    km.fit(tfidf_matrix)
    clusters = km.labels_.tolist()

    data = {'titles': titles, 'text': texts, 'clusters': clusters}

    frame = pd.DataFrame(data, index=[clusters], columns=['titles', 'text', 'clusters'])
    print(frame)

    print("Top terms per cluster:")
    print()
    # sort cluster centers by proximity to centroid
    order_centroids = km.cluster_centers_.argsort()[:, ::-1]

    for i in range(num_clusters):
        print("Cluster %d words:" % i, end='')

        for ind in order_centroids[i, :10]:  # replace 6 with n words per cluster
            print(' %s' % vocabulary[ind], end='')
        print()
        print("Cluster %d titles:" % i)
        for title in frame.ix[i]['titles'].values.tolist():
            print(' %s,' % title)
        print()  # add whitespace
        print()  # add whitespace
