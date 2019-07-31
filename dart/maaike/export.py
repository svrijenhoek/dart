import csv
from datetime import datetime as dt
from dart.handler.elastic.article_handler import ArticleHandler
from dart.handler.elastic.connector import ElasticsearchConnector
from dart.models.Article import Article


connector = ElasticsearchConnector()
searcher = ArticleHandler(connector)


def make_txt(title, date, author, source, text):
    body = "{}\n{}, {}, {}\n\n{}".format(title, date, author, source, text)
    filename = source + '_' + date
    filename = filename.replace(":", "-")
    try:
        with open("C:\\Users\\Sanne\\PycharmProjects\\DART\\output\\Weinstein\\"+filename+".txt", "w") as text_file:
            text_file.write(body)
    except UnicodeEncodeError:
        pass


source = "C:\\Users\\Sanne\\PycharmProjects\\DART\\data\\input.csv"
with open(source, 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in reader:
        try:
            id = row[2].replace("\"", "")
            document = searcher.get_by_id(id)
            date = document.publication_date
            title = document.title
            text = document.text
            try:
                author = document.author
            except KeyError:
                author = ''
            source = document.doctype
            make_txt(title, date, author, source, text)
        except IndexError:
            print(id)
            pass
